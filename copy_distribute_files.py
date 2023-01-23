import shutil
import os
import time

start = time.time()


def main():
    #print(f"Start copy job at {start}")
    for i in os.listdir("../labelling_outputs/"):
        src = f"../labelling_outputs/{i}/"
        for j in os.listdir(src):
            src_file = f"{src}/{j}"
            dst_fr = f"./labelling/FR_output/{j}"
            dst_label = f"./labelling/GT_check/{j}"
            dst_image = f"./labelling/images/{j}"

            if ".ocr.json" in j:
                shutil.copyfile(src_file, dst_fr)
            if ".labels.json" in j:
                shutil.copyfile(src_file, dst_label)
            if j.endswith(".PNG") or j.endswith(".jpeg"):
                shutil.copyfile(src_file, dst_image)


            end = time.time()
    #print(f"End copy job at {end}")

if __name__ == "__main__":
    main()