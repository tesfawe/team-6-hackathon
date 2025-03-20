import numpy as np
import os
from collections import defaultdict

# Threshold for x_center similarity to consider them "stacked"
x_threshold = 0.02
folder_path = "./YOLO_txts"  

# Get all .txt files in the folder and sort them alphabetically
txt_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".txt")])

# Iterate over sorted .txt files
for filename in txt_files:
    file_path = os.path.join(folder_path, filename)

    try:
        yolo_data = np.loadtxt(file_path)

        if yolo_data.size == 0:  
            print(f"{filename}: No data found.")
            continue

        if yolo_data.ndim == 1:  # Handle single-line YOLO files
            yolo_data = np.expand_dims(yolo_data, axis=0)

        # Group bounding boxes by x_center similarity
        x_groups = defaultdict(list)

        for entry in yolo_data:
            class_id, x_center, y_center, width, height = entry
            found_group = False

            for key in x_groups.keys():
                if abs(x_center - key) < x_threshold:
                    x_groups[key].append((x_center, y_center, width, height))
                    found_group = True
                    break

            if not found_group:
                x_groups[x_center].append((x_center, y_center, width, height))

        # Find the maximum number of stacked boxes
        max_stacked = max(len(boxes) for boxes in x_groups.values())
        print(f"{filename}: {max_stacked}")

    except Exception as e:
        print(f"Error processing {filename}: {e}")

