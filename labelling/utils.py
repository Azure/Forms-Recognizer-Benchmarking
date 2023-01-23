import json
import pandas as pd
import numpy as np
import os


def convert_inches_pixel(a):

    """
    Convert inch based bounding boxes to pixel based bounding boxes

    input:
        a = array of inch based bbox
    output:
        converted bouding boxS

    """

    # hard coded -> in case of corrections of measurements, please change
    pixel_conv = 1
    

    x =  a[::2]
    y = list(set(a) ^ set (x))

    # print('\n\nconverting...\n\n')
    # print(a)
    # print(x)
    # print(y)

    
    # for better interpretation I have created a dict
    try:
        k = {
            "x_max": round(max(x) * pixel_conv), 
            "y_max": round(max(y) * pixel_conv),  
            "x_min": round(min(x) * pixel_conv),
            "y_min": round(min(y) * pixel_conv)
            }
    except ValueError:
        y = a[1::2]
        k = {
            "x_max": round(max(x) * pixel_conv), 
            "y_max": round(max(y) * pixel_conv),  
            "x_min": round(min(x) * pixel_conv),
            "y_min": round(min(y) * pixel_conv)
            }
        
    w = k["x_max"] - k["x_min"]
    h = k["y_max"] - k["y_min"]

    # choose elements in correspondence with target format bboxes
    k2 = {
        "x_min":  k["x_min"], #upper left
        "y_min":  k["y_min"],  #upper left
        "w": w ,#width
        "h": h #height
        }
    
    return list(k2.values())


def convert_inches_pixel_normalized_vector(a, pixel_conv_x, pixel_conv_y):

    """
    Convert inch based bounding boxes to pixel based bounding boxes

    input:
        a = array of inch based bbox
        pixel_conv = array of inch based bbox
    output:
        converted bouding boxS

    """

    x =  a[::2]
    y = list(set(a) ^ set (x))

    # print('\n\nconverting...\n\n')
    # print(a)
    # print(x)
    # print(y)

    
    # for better interpretation I have created a dict
    k = {
        "x_max": round(max(x) * pixel_conv_x), 
        "y_max": round(max(y) * pixel_conv_y),  
        "x_min": round(min(x) * pixel_conv_x),
        "y_min": round(min(y) * pixel_conv_y)}
    
    w = k["x_max"] - k["x_min"]
    h = k["y_max"] - k["y_min"]

    # choose elements in correspondence with target format bboxes
    k2 = {
        "x_min":  k["x_min"], #upper left
        "y_min":  k["y_min"],  #upper left
        "w": w ,#width
        "h": h #height
        }
    
    return list(k2.values())


def format_json_sublevel(df, index):

    """
    Format structued table into list of dictionaries.

    input: 
        df = strutcured dataframe
        index = iterator
    output:
        strtuctured dictionary 
    """

    return {"text": df["text"].values[index], 
    "confidence": df["confidence"].values[index],  
    "bbox": df["bbox_formatted"].values[index],  
    "page_index": df["page"].values[index]}

def format_json_sublevel_label(df, index):

    """
    Format structued table into list of dictionaries.

    input: 
        df = strutcured dataframe
        index = iterator
    output:
        strtuctured dictionary 
    """

    return {"text": df["text"].values[index], 
    "bbox": df["bbox_formatted"].values[index],  
    "page_index": df["page"].values[index]}

def format_table_sublevel(df, index):

    """
    Format structued table into list of dictionaries.

    input: 
        df = strutcured dataframe
        index = iterator
    output:
        strtuctured dictionary 
    """

    return {"text": df["text"][index], 
    "confidence": df["confidence"][index], 
    "bbox": df["bbox_formatted"][index],  
    "row": df["rowIndex"][index], 
    "col": df["columnIndex"][index],
    "page_index": df["page"][index]}

def convert_to_dict_list(d):

    """"
    Dump dictionary into a list to preserve format
    """
    
    return [d]

def parse_text_labels(base_data):

    """
    
    Extracts text from document

    input:
        base table: all levels of json that contain text
    output: see return statement

    """

    text_list2 = []
    bb_list2 = []
    confidence_list2 = []
    page_list2 =[]
    level_cat = []
    level2 = []


    for ii in range(len(base_data)): #iterates number of pages
        sample = base_data[ii]["value"]
        level_cat = base_data[ii]["label"]

        #Character level
        for j in range(len(sample)): #iterate thtough each entry of the json
            sample2 = sample[j]
            text_list2.append(sample2["text"])
            bb_list2.append(sample2["boundingBoxes"][0])
            page_list2.append(sample2["page"])
            level2.append(level_cat)

    return page_list2, text_list2,bb_list2, level2


def parse_text_ocr(base_data):

    """
    
    Extracts text from document

    input:
        base table: all levels of json that contain text
    output: see return statement

    """

    text_list2 = []
    bb_list2 = []
    confidence_list2 = []
    page_list2 =[]
    level2 = []

    for ii in range(len(base_data)): #iterates number of pages
        sample = base_data
        #Character level
        for j in range(len(sample)): #iterate thtough each entry of the json
            sample2 = sample[j]["words"]
            try: 
                for n in range(len(sample2)): #iterate through each sub-level contained in words
                    text_list2.append(sample2[n]["content"])
                    bb_list2.append(sample2[n]["polygon"])
                    confidence_list2.append(sample2[n]["confidence"])
                    page_list2.append(base_data[ii]["pageNumber"])
            except KeyError:
                text_list2.append(sample2["content"])
                bb_list2.append(sample2["polygon"])
                confidence_list2.append(sample2["confidence"])
                page_list2.append(base_data[ii]["pageNumber"])
                level2.append("body")

    return page_list2, text_list2,bb_list2, confidence_list2, level2


def parse_tables(base_data_):
    
    """
    Parses document's table and outputs lists that contain content

    input: table level of data
    output: see return statement

    """
    text_list3 = [] 
    bb_list3 = []
    columnIndex = []
    rowIndex = []
    tableIndex = []
    page_index = []
    confidence_ = []
    # Table level
    for kk in range(len(base_data_)): # dependent on the number of tables
        sample_big = base_data_[kk]["tables"] # iterate by table elements

        for nn in range(len(sample_big)): #iterate table by table
            sample_ = sample_big[nn]["cells"]

            for jj in range(len(sample_)):  #iterate table by table content
                text_list3.append(sample_[jj]["text"])
                bb_list3.append(sample_[jj]["boundingBox"])
                columnIndex.append(sample_[jj]["columnIndex"])
                rowIndex.append(sample_[jj]["rowIndex"])
                confidence_.append(None)

                #populate higher level variables for consistency(table level)
                tableIndex.append(nn)
                page_index.append(base_data_[kk]["page"])
    return page_index, text_list3,bb_list3, confidence_, columnIndex, rowIndex, tableIndex

#format on per table basis
def iterate_format_tables(filter_table, m):
    tables_sub = {}
    tables_sub_list = []

    for u in list(filter_table.index):
        tables_sub_list.append(format_table_sublevel(filter_table, u))
    tables_sub = {str(m) : tables_sub_list}
    return tables_sub


def iterate_table_per_page(df_table_page):
    tables_formatted = []
    for m in df_table_page["tableIndex"].unique(): #iterate by table index
        filter_table = df_table_page[df_table_page["tableIndex"] == m]
        tables_formatted.append(iterate_format_tables(filter_table, m))
    return tables_formatted

def reformat_tables_into_dict_per_page(tables_by_page_formatted):
    """
    Converts list of dictionaries into dictionar by iterating through each table
    input:
        list if dicts of all tables on ONE page
    output:
        flattened dict
    """
    rearrage_table_per_page = {}
    for table_number in range(len(tables_by_page_formatted)):
        rearrage_table_per_page.update({table_number: list(tables_by_page_formatted[table_number].values())[0]})
    return rearrage_table_per_page

def merge_dicts(text_by_page_formatted, tables_by_page_formatted):
    d = {}
    d_sub = {}
    d["text"] = {}
    d["table"] = {}

    ###############################
    ############ TEXT #############
    ###############################
    d_sub = text_by_page_formatted

    ###############################
    ######### FULL TABLE ##########
    ###############################
    # Get text elements
    d["text"] = d_sub

    # Get table elements
    try:
        d["table"] = reformat_tables_into_dict_per_page(tables_by_page_formatted)
    except NameError:
        d["table"] = {} #if no table present, add empty dict
    return d


def compute_closest_bbox(unmatching_df_gt_only, unmatching_bboxes_df_all):
    """
    Not all bounding boxes have a correct conversion for the normalised matrix returned by the FR labelling tool. 
    For those bounding boxes, we need to find the closest bounding box to the one from the FR extracted value and overwrite the normalised bounding box value.
    This will later allow us to join the extracted values and ground truth values on the bounding box.

    inputs:
        unmatching_df_gt_only: This is the subset of ground truth items (values) that do not have a corresponding extracted pair via the bounding box join key
        unmatching_df_gt_only: Those are all items (ground truth and extracted values) that did not get joined as tgere us no bounding box pair

    output:
        clostest_items_df: contains the lookup keys for the bounding box to be replaced

    """
    bbox_proximity = []
    closet_items_list = []

    for subset in list(unmatching_df_gt_only.filename.unique()):
        unmatching_df_gt_only_subset = unmatching_df_gt_only[unmatching_df_gt_only.filename == subset]
        print(subset)
        print(len(unmatching_df_gt_only_subset))
        try:
            for i in unmatching_df_gt_only_subset["bbox_formatted_ground_truth"]:
                for j in unmatching_bboxes_df_all["bbox_formatted_extracted"]:
                    try:
                        distance = [a_i^2 - b_i^2 for a_i, b_i in zip(i, j)]
                        distance_sum = sum(distance)
                        bbox_proximity.append([distance, distance_sum, j, i])
                    except:
                        pass
            
            tt = pd.DataFrame(bbox_proximity)
            tt.columns = ["coordinate_diff", "squared_sum_diff", "bbox_formatted_extracted", "bbox_formatted_ground_truth"]
            
            # Find the closest item
            for jj in unmatching_df_gt_only_subset.bbox_formatted_ground_truth: 
                tt_closest = tt[tt.bbox_formatted_ground_truth.astype(str) == str(jj)]
                tt_closest = tt_closest.iloc[(tt_closest['squared_sum_diff']-0).abs().argsort()[:1]]
                closet_items_list.append(tt_closest)
                del tt_closest, tt
        except:
            pass
    #clostest_items_df = pd.concat(closet_items_list)
    return closet_items_list



def compute_closest_bbox(unmatching_df_gt_only, unmatching_bboxes_df_all):
    """
    Not all bounding boxes have a correct conversion for the normalised matrix returned by the FR labelling tool. 
    For those bounding boxes, we need to find the closest bounding box to the one from the FR extracted value and overwrite the normalised bounding box value.
    This will later allow us to join the extracted values and ground truth values on the bounding box.

    inputs:
        unmatching_df_gt_only: This is the subset of ground truth items (values) that do not have a corresponding extracted pair via the bounding box join key
        unmatching_df_gt_only: Those are all items (ground truth and extracted values) that did not get joined as tgere us no bounding box pair

    output:
        clostest_items_df: contains the lookup keys for the bounding box to be replaced

    """
    bbox_proximity = []
    closet_items_list = []

    for subset in list(unmatching_df_gt_only.filename.unique()):
        unmatching_df_gt_only_subset = unmatching_df_gt_only[unmatching_df_gt_only.filename == subset]
        unmatching_bboxes_df_all = unmatching_bboxes_df_all.dropna(subset=["bbox_formatted_extracted"])
        unmatching_df_all_subset = unmatching_bboxes_df_all[unmatching_bboxes_df_all.filename == subset]

        try:
            for i in unmatching_df_gt_only_subset["bbox_formatted_ground_truth"]:
                for j in unmatching_df_all_subset["bbox_formatted_extracted"]:
                    i = literal_eval(i)
                    j = literal_eval(j)
                    distance = [a_i^2 - b_i^2 for a_i, b_i in zip(i, j)]
                    distance_sum = sum(distance)
                    bbox_proximity.append([distance, distance_sum, j, i, subset])
                    tt = pd.DataFrame(bbox_proximity)
                    tt.columns = ["coordinate_diff", "squared_sum_diff", "bbox_formatted_extracted", "bbox_formatted_ground_truth", "filename"]

                    
                    # Find the closest item
                    for jj in unmatching_df_gt_only_subset.bbox_formatted_ground_truth: 
                        tt_closest = tt[tt.bbox_formatted_ground_truth.astype(str) == str(jj)]
                        tt_closest = tt_closest.iloc[(tt_closest['squared_sum_diff']-0).abs().argsort()[:1]]
                        closet_items_list.append(tt_closest)
                        del tt_closest, tt
        except:
            pass

    clostest_items_df = pd.concat(closet_items_list)
    return clostest_items_df


def parse_text_ocr_entities(data_predicted):

    """
    
    Extracts text from document

    input:
        base table: all levels of json that contain text
    output: dataframe with a parsed, structured output

    """
    text_list2 = []
    bb_list2 = []
    confidence_list2 = []
    page_list2 =[]
    key = []

    base_data = data_predicted["analyzeResult"]["documents"][0]["fields"]


    for i in base_data.keys():
        try:
            sample = base_data[i]
            key.append(i)
            text_list2.append(sample["content"])
            bb_list2.append(sample["boundingRegions"][0]["polygon"])
            confidence_list2.append(sample["confidence"])
            page_list2.append(sample["boundingRegions"][0]["pageNumber"])
        except KeyError:
            pass

    # Format text into target format per page
    df2 = pd.DataFrame([page_list2, text_list2,bb_list2, confidence_list2, key]).T
    df2.columns = ["page", "text","bbox", "confidence", "level"]
    df = df2.copy()
    tmp = []
    for i in range(len(df)):
        try:
            tmp.append(convert_inches_pixel(list(df["bbox"].iloc[i]))) #df["bbox"] 
        except:
            tmp.append(None)

    df["bbox_formatted"] = tmp

    return df