import json
import pandas as pd
import numpy as np
from utils import *
import glob
import re

files_ocr = glob.glob('./FR_output/*.json')

df_all = []

for ii in files_ocr:
    with open(f"./{ii}", 'r', encoding="utf8") as f:
        data = json.load(f)
    print("Processing ", ii)

    ##################
    ## PARSE DOCUMENT TEXT
    ##################

    base_data = data["analyzeResult"]["pages"]

    #Parse original output
    page_list2, text_list2,bb_list2, confidence_list2, level2 = parse_text_ocr(base_data)


    # Format text into target format per page
    df2 = pd.DataFrame([page_list2, text_list2,bb_list2, confidence_list2, level2]).T
    df2.columns = ["page", "text","bbox", "confidence", "level"]
    regx = re.compile("([^\/]+$)")
    file_name = regx.findall(ii)[0]
    df2["filename"] = file_name
    df = df2.copy()
    #df = pd.concat([df1, df2], axis=0)
    assert len(df) == len(df[~df.confidence.isna()])
    # convert bounding boxes
    df["bbox_formatted"] = [convert_inches_pixel(list(df["bbox"].iloc[i])) for i in range(len(df))] #df["bbox"] 
    df.sample(3)

    # Iterate by page
    text_by_page_formatted = []
    for i in df["page"].unique():
        df_page= df[df.page == i]
        text_by_page_formatted.append([format_json_sublevel(df_page, u) for u in range(len(df_page))])


    ##################
    ## PARSE TABLES
    ##################

    try: 
        base_data_ = data["analyzeResult"]["pageResults"] #THIS IS WHEN TABLES ARE PRESENT IN THE DOCUMENT

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
        assert len(text_by_page_formatted) == len(tables_by_page_formatted)
        d_all_pages = [merge_dicts(text_by_page_formatted[ii], tables_by_page_formatted[ii]) for ii in range(len(text_by_page_formatted))]
    except:
        pass
        d_all_pages = text_by_page_formatted

    ##################
    ## SAVE FILE
    ##################
    with open(f'./post_conversion_ocr/{file_name}', 'w', encoding='utf8') as f:
        json.dump(d_all_pages, f, ensure_ascii=False)
    df_all.append(df)

#WRITE CSV FILES CONTAINING RECOGNISED LABELS
df_all = pd.concat(df_all)
df_all.drop(columns=["bbox"]).to_csv(f"./eval_tables/FR_extracts/forms_recognizer_prediction_files.csv", index=False)