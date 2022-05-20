import pathlib
import pandas as pd
from computeLdaTsne import lda_analysis
from wordcloud import STOPWORDS
import re
import json

DATA_PATH = pathlib.Path(__file__).parent.resolve()
EXTERNAL_STYLESHEETS = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
FILENAME = "data/dataset_covid19_coaid/consolidado.tsv"
GLOBAL_DF = pd.read_csv(DATA_PATH.parent.joinpath(FILENAME), sep="\t")

"""
In order to make the graphs more useful we decided to prevent some words from being included
"""
ADDITIONAL_STOPWORDS = [
    "COVID",
    "COVID-19",
    "coronavirus",
    "covid"
]
for stopword in ADDITIONAL_STOPWORDS:
    STOPWORDS.add(stopword)


def add_stopwords(selected_bank):
    """
    In order to make a more useful NLP-data based graphs, it helps to remove
    common useless words. In this case XXXX usually represents a redacted name
    We also exlude more standard words defined in STOPWORDS which is provided by
    the Wordcloud dash component.
    """
    selected_bank_words = re.findall(r"[\w']+", selected_bank)
    for word in selected_bank_words:
        STOPWORDS.add(word.lower())

    print("Added %s stopwords:" % selected_bank)
    for word in selected_bank_words:
        print("\t", word)
    return STOPWORDS


def precompute_all_lda():
    """ QD function for precomputing all necessary LDA results
     to allow much faster load times when the app runs. """

    failed_annots = []
    counter = 0
    

    #GLOBAL_DF["created_at"] = GLOBAL_DF["created_at"].astype("datetime64[ns]")
    #group_by_timefreq = [part for _, part in GLOBAL_DF.groupby(pd.Grouper(key="created_at", freq="M"))] 
    

    GLOBAL_DF["created_at"] = GLOBAL_DF["created_at"].astype("datetime64[ns]")
    annot_names = GLOBAL_DF["source"].value_counts().keys().tolist()

    results = {}

    #for group_time_df in group_by_timefreq:
    for annot in annot_names:
        try:
            print("analyzing LDA for timegroup: ", annot)
            tweet_by_annot_df = GLOBAL_DF[GLOBAL_DF["source"] == annot] 
            tsne_lda, lda_model, topic_num, df_dominant_topic = lda_analysis(
                tweet_by_annot_df, list(STOPWORDS)
            )

            topic_top3words = [
                (i, topic)
                for i, topics in lda_model.show_topics(formatted=False)
                for j, (topic, wt) in enumerate(topics)
                if j < 3
            ]

            df_top3words_stacked = pd.DataFrame(
                topic_top3words, columns=["topic_id", "words"]
            )
            df_top3words = df_top3words_stacked.groupby("topic_id").agg(", \n".join)
            df_top3words.reset_index(level=0, inplace=True)

            # print(len(tsne_lda))
            # print(len(df_dominant_topic))
            tsne_df = pd.DataFrame(
                {
                    "tsne_x": tsne_lda[:, 0],
                    "tsne_y": tsne_lda[:, 1],
                    "topic_num": topic_num,
                    "doc_num": df_dominant_topic["Document_No"],
                }
            )

            topic_top3words = [
                (i, topic)
                for i, topics in lda_model.show_topics(formatted=False)
                for j, (topic, wt) in enumerate(topics)
                if j < 3
            ]

            df_top3words_stacked = pd.DataFrame(
                topic_top3words, columns=["topic_id", "words"]
            )
            df_top3words = df_top3words_stacked.groupby("topic_id").agg(", \n".join)
            df_top3words.reset_index(level=0, inplace=True)

            results[str(annot)] = {
                "df_top3words": df_top3words.to_json(),
                "tsne_df": tsne_df.to_json(),
                "df_dominant_topic": df_dominant_topic.to_json(),
            }

            counter += 1
        except Exception as e:
            print("Not enough data for annot: ", annot)
            print(str(e))
            failed_annots.append(annot)

    with open("../data/dataset_covid19_coaid/precomputed.json", "w+") as res_file:
        json.dump(results, res_file)

    print("DONE")
    print("did %d tweets-annots" % counter)
    print("failed %d:" % len(failed_annots))
    for fail in failed_annots:
        print(fail)



if __name__ == "__main__":
    precompute_all_lda()
