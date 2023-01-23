echo "copy files"
python copy_distribute_files.py

cd labelling

echo "processing labels"
python format_process_files_labels.py

echo "processing ocr"
python format_process_files_ocr.py

echo "evaluating performance"
python evaluate_performance_ocr.py