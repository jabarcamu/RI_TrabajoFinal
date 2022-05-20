
import gzip
import shutil
import os
import wget
import csv
import linecache
from shutil import copyfile
import numpy as np
import pandas as pd


#dataset_path = "../datasets/2021-01-20_clean-dataset.tsv.gz"

folder_tsv = "../datasets/2021-01-20_clean.tsv"
#unzip the folder
#with gzip.open(dataset_path,"rb") as f_in:
#    with open(folder_tsv, "wb") as f_out:
#        shutil.copyfileobj(f_in, f_out)

#delete the compressed GZ file
#os.unlink("clean-dataset.tsv.gz")

#Gets all possible languages from dataset
df = pd.read_csv(folder_tsv, sep="\t")
lang_list = df.lang.unique()
land_list = sorted(np.append(lang_list,"all"))

# Idiom choosen is "es"

filtered_language = "en"

# if no language specified, it will get all records from dataset
if filtered_language == "":
    copyfile(folder_tsv, "clean-dataset-filtered.tsv")
# if language specified, it will create another tsv file with  the filtered records
else:
    filtered_tw = list()
    current_line = 1
    with open(folder_tsv) as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")

        if current_line == 1:
            filtered_tw.append(linecache.getline(folder_tsv,current_line))
        
            for line in tsvreader:
                if line[3] == filtered_language:
                    filtered_tw.append(linecache.getline(folder_tsv,current_line))
                current_line += 1
    print("\033[1mShowing first 5 tweets from the filtered dataset\033[0m")
    print(filtered_tw[1:(6 if len(filtered_tw) > 6 else len(filtered_tw))])

    with open("clean-dataset-filtered.tsv", "w") as f_output:
        for item in filtered_tw:
            f_output.write(item)

    
