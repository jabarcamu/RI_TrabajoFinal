# ========== (c) JP Hwang 2020-03-17  ==========

import logging

# ===== START LOGGER =====
logger = logging.getLogger(__name__)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
root_logger.addHandler(sh)

import pandas as pd
import plotly.express as px
from sklearn.manifold import TSNE

desired_width = 320
pd.set_option("display.max_columns", 20)
pd.set_option("display.width", desired_width)


def main():

    comp_df = pd.read_csv(
        "data/customer_complaints_narrative_sample.csv.gz", index_col=0
    )
    
    fig = px.histogram(comp_df, x="datetime", template="plotly_white", title="Complaint counts by date")

    fig.update_xaxes(categoryorder="category descending", title="Date").update_yaxes(title="Number of Complaints")

    fig.update_layout(width=1200, height=500)
    fig.show()

    comp_df.head()
if __name__ == "__main__":
    main()
