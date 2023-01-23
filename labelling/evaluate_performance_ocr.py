import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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


extracted_vals = pd.read_csv("./eval_tables/FR_extracts/forms_recognizer_prediction_files.csv")
ground_truth = pd.read_csv("./eval_tables/GT_annotations/ground_truth_files.csv")

extracted_vals['bbox_formatted'] = extracted_vals['bbox_formatted'].apply(lambda x: "".join(str(x)))
ground_truth['bbox_formatted'] = ground_truth['bbox_formatted'].apply(lambda x: "".join(str(x)))

#MERGE DATASET
combined_df = pd.merge(ground_truth,extracted_vals, on="bbox_formatted", suffixes=["_extracted", "_ground_truth"], how="left")
combined_df["text_ground_truth"] = combined_df["text_ground_truth"].fillna("")
combined_df["text_extracted"] = combined_df["text_extracted"].fillna("<MISSED VALUE>")
combined_df["word_similarity"] = [fuzzy_score(combined_df["text_extracted"][i], combined_df["text_ground_truth"][i]) for i in range(len(combined_df))]

#CREATE CONSISTENCY FOR THE CATEGORIES DURING LABELLING
# category_mapping = {
#     "REMAP IF NEEDED"
# }
# combined_df = combined_df.replace({"level_extracted": category_mapping})


#PREPARE FILES FOR RESULT LOGGING
aggregated_file = combined_df[["word_similarity", "filename_extracted"]].groupby(["filename_extracted"]).mean().reset_index()
aggregated_file_level = combined_df[["word_similarity", "filename_extracted", "level_extracted"]].groupby(["filename_extracted","level_extracted"]).mean().reset_index()
aggregated_level = combined_df[["word_similarity", "level_extracted"]].groupby(["level_extracted"]).mean().reset_index()

combined_df.to_csv("./eval_tables/evaluation_combined/results_transactions.csv",index=False)
aggregated_file.to_csv("./eval_tables/evaluation_combined/results_aggregated.csv", index=False)
aggregated_file_level.to_csv("./eval_tables/evaluation_combined/results_aggregated_level.csv", index=False)
aggregated_level.to_csv("./eval_tables/evaluation_combined/results_aggregated_level_only.csv", index=False)