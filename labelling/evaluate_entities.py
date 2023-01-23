#!/usr/bin/env python
# coding: utf-8

# In[14]:


import json
import pandas as pd
import numpy as np
import os
from utils import *
import re

import glob
import itertools
from PIL import Image
from fuzzywuzzy import fuzz



def fuzzy_score(text, value):
    """
    Function for fuzzy matching given two strings

    Args:
        text (string): ocr data text
        value (string): entity label

    Returns:
        float : Fuzzy match score
    """

    return fuzz.ratio(text, value)


source_folder = '../../test_data/'

gt_labels = glob.glob(f'{source_folder}test_labels/*labels.json')
predicted_labels = glob.glob(f'{source_folder}test_outputs/*.json')
images_test = [glob.glob(e) for e in [f'{source_folder}test_images/*.jpeg', f'{source_folder}test_images/*.PNG', f'{source_folder}test_images/*.png']]
images_test = list(itertools.chain(*images_test)) #flatten the list

df_all = []

for jj, ii in enumerate(images_test):

    regx = re.compile("([^\/]+$)")
    file_name = regx.findall(ii)[0]


    idx = jj
    filename_gt = gt_labels[idx]
    filename_label = predicted_labels[idx]
    test_img = images_test[idx]


    with open(f"./{filename_gt}", 'r', encoding="utf8") as f:
        data_label = json.load(f)

    with open(f"./{filename_label}", 'r', encoding="utf8") as f:
        data_predicted = json.load(f)


    img = Image.open(test_img)
    width, height = img.size


    assert len(gt_labels) == len(predicted_labels) == len(images_test)


    df = parse_text_ocr_entities(data_predicted)

    #CREATE CONSISTENCY FOR THE CATEGORIES DURING LABELLING
    category_mapping_output = {"From": "Exporter Name",
    "To": "Recipient Name",
    }

    df = df.replace({"level": category_mapping_output})
    df = df.replace('\n',' ', regex=True) #clean up some messy strings

    #PARSE JSON OUTPUT

    base_data = data_label["labels"]

    #Parse original output
    page_list2, text_list2,bb_list2, level_cat = parse_text_labels(base_data)

    # Format text into target format per page
    df2 = pd.DataFrame([page_list2, text_list2,bb_list2, level_cat]).T
    df2.columns = ["page", "text","bbox", "level"]
    df_label = df2.copy()

    # convert bounding boxes
    df_label["bbox_formatted"] = [convert_inches_pixel_normalized_vector(list(df_label["bbox"].iloc[i]), pixel_conv_x=width, pixel_conv_y=height) for i in range(len(df_label))]


    # Iterate by page
    text_by_page_formatted_label = []
    for i in df_label["page"].unique():
        df_label_page= df_label[df_label.page == i]
        text_by_page_formatted_label.append([format_json_sublevel_label(df_label_page, u) for u in range(len(df_label_page))])


    # In[5]:


    #CREATE CONSISTENCY FOR THE CATEGORIES DURING LABELLING
    # category_mapping = {"..."}
    # df_label = df_label.replace({"level": category_mapping})
    
    df_label.rename(columns={"text": "text_ground_truth"}, inplace=True)

    # group ground truth labels into one concatenated string per category rather than token by token
    tt = df_label[['text_ground_truth','level']].fillna(" ")
    tt = tt.groupby(['level'], as_index=False).agg({'text_ground_truth': ' '.join})

    #MERGE GROUND TRUTH AND PREDICTED VALUE BY LEVEL INTO 1 FILE
    tt = tt.merge(df, how="outer", left_on="level", right_on="level")
    tt = tt.fillna(" ")

    # COMPUTE WORD SIMILARITY
    tt["word_similarity"] = [fuzzy_score(tt["text_ground_truth"][i], tt["text"][i]) for i in range(len(tt))]

    # ADD FILENAME
    tt["filename_extracted"] = file_name
    tt.rename(columns={"level": "level_extracted"}, inplace=True)
    df_all.append(tt)


#WRITE CSV FILE CONTAINING GROUND TRUTH LABELS
df_all = pd.concat(df_all)
df_all.to_csv(f"./eval_tables/entity_evaluation/results_transaction_entity.csv", index=False)


#PREPARE FILES FOR RESULT LOGGING
path_ = "./eval_tables/entity_evaluation/"
aggregated_file = pd.read_csv(f"{path_}results_transaction_entity.csv")

aggregated_file[["word_similarity", "filename_extracted"]].groupby(["filename_extracted"]).mean().reset_index()
aggregated_file_level = aggregated_file[["word_similarity", "filename_extracted", "level_extracted"]].groupby(["filename_extracted","level_extracted"]).mean().reset_index()
aggregated_level = aggregated_file[["word_similarity", "level_extracted"]].groupby(["level_extracted"]).mean().reset_index()

aggregated_file.to_csv(f"{path_}results_aggregated_entities.csv", index=False)
aggregated_file_level.to_csv(f"{path_}results_aggregated_level_entities.csv", index=False)
aggregated_level.to_csv(f"{path_}results_aggregated_level_only_entities.csv", index=False)


