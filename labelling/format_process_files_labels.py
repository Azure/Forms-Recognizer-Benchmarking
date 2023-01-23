import json
import pandas as pd
import numpy as np
from utils import *
import glob
import re
from PIL import Image


files_ocr = glob.glob('./GT_check/*.json')

df_all = []

for ii in files_ocr:
    with open(f"./{ii}", 'r', encoding="utf8") as f:
        data_label = json.load(f)
    print("Processing ", ii)

    ##################
    ## PARSE DOCUMENT TEXT IN LABELLED DOCUMENTS
    ##################
    base_data = data_label["labels"]

    #Parse original output
    page_list2, text_list2,bb_list2, level2 = parse_text_labels(base_data)

    # Format text into target format per page
    df2 = pd.DataFrame([page_list2, text_list2,bb_list2, level2]).T
    df2.columns = ["page", "text","bbox", "level"]
    regx = re.compile("([^\/]+$)")
    file_name = regx.findall(ii)[0]
    df2["filename"] = file_name
    df_label = df2.copy()

    # convert bounding boxes
    regx_img_name_png = re.compile("(^(.*?)PNG)")
    regx_img_name_jpeg = re.compile("(^(.*?)jpeg)")
    regx_img = re.compile("([^\/]+$)")

    if ".PNG" in ii:
        img_path = regx_img_name_png.findall(ii)[0][0]
    if ".jpeg" in ii:
        img_path = regx_img_name_jpeg.findall(ii)[0][0]
    
    img_name = regx_img.findall(img_path)[0]
    im = Image.open(f'./images/{img_name}')
    width, height = im.size
    del im

    # convert bounding boxes
    df_label["bbox_formatted"] = [convert_inches_pixel_normalized_vector(list(df_label["bbox"].iloc[i]), pixel_conv_x=width, pixel_conv_y=height) for i in range(len(df_label))]

    # Iterate by page
    text_by_page_formatted_label = []
    for i in df_label["page"].unique():
        df_label_page= df_label[df_label.page == i]
        text_by_page_formatted_label.append([format_json_sublevel_label(df_label_page, u) for u in range(len(df_label_page))])


    ##################
    ## PARSE TABLES
    ##################

    try: 
        base_data_ = data_label["analyzeResult"]["pageResults"] #THIS IS WHEN TABLES ARE PRESENT IN THE DOCUMENT

        try:
            page_index, text_list3,bb_list3, confidence_, columnIndex, rowIndex, tableIndex =  parse_tables(base_data_)
            df_table = pd.DataFrame([page_index, text_list3,bb_list3, confidence_, columnIndex, rowIndex, tableIndex]).T
            df_table.columns = ["page", "text","bbox", "confidence", "columnIndex", "rowIndex", "tableIndex"]
            df_table["bbox_formatted"] = [convert_inches_pixel(list(df_table["bbox"].iloc[i])) for i in range(len(df_table))]

            ###############################
            ############ TABLE ############
            ###############################
            
            # iterate per page per table
            tables_by_page_formatted = []
            for i in df_table.page.unique():
                tables_by_page_formatted.append(iterate_table_per_page(df_table[df_table.page == i]))
            
        except KeyError:
            pass
    except KeyError:
        #IF NO TABLES PRESENT
        pass

    ##################
    ## FORMAT DOCUMENT
    ##################
    try:
        assert len(text_by_page_formatted_label) == len(tables_by_page_formatted)
        d_all_pages = [merge_dicts(text_by_page_formatted_label[ii], tables_by_page_formatted[ii]) for ii in range(len(text_by_page_formatted_label))]
    except:
        pass
        d_all_pages = text_by_page_formatted_label

    ##################
    ## SAVE FILE
    ##################
    with open(f'./post_conversion_label/{file_name}', 'w', encoding='utf8') as f:
        json.dump(d_all_pages, f, ensure_ascii=False)
    df_all.append(df_label)

#WRITE CSV FILE CONTAINING GROUND TRUTH LABELS
df_all = pd.concat(df_all)
df_all.drop(columns=["bbox"]).to_csv(f"./eval_tables/GT_annotations/ground_truth_files.csv", index=False)