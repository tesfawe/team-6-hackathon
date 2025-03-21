import os
import random
import shutil

# Define dataset paths (add paths for 3 datasets)
dataset_dirs = ["data/original data", "data/augmented data", "data/oscd data"]

# Define paths for merging and final split
merged_image_dir = "data/merged_dataset/images"
merged_label_dir = "data/merged_dataset/labels"
output_dir = "data/dataset_split"

# Create merged directories
os.makedirs(merged_image_dir, exist_ok=True)
os.makedirs(merged_label_dir, exist_ok=True)

# Merge images and labels from all datasets
for dataset in dataset_dirs:
    image_dir = os.path.join(dataset, "images")
    label_dir = os.path.join(dataset, "labels")

    for file in os.listdir(image_dir):
        shutil.copy(os.path.join(image_dir, file), os.path.join(merged_image_dir, file))
        label_file = file.replace(".jpeg", ".txt").replace(".png", ".txt")
        
        if os.path.exists(os.path.join(label_dir, label_file)):
            shutil.copy(os.path.join(label_dir, label_file), os.path.join(merged_label_dir, label_file))

print("Datasets merged successfully!")

# Create train, val, and test output directories
for split in ["train", "val", "test"]:
    os.makedirs(f"{output_dir}/images/{split}", exist_ok=True)
    os.makedirs(f"{output_dir}/labels/{split}", exist_ok=True)

# Get all image names
image_files = os.listdir(merged_image_dir)

# Shuffle and split
random.shuffle(image_files)
train_split = int(0.8 * len(image_files))
val_split = int(0.9 * len(image_files))

train_files = image_files[:train_split]
val_files = image_files[train_split:val_split]
test_files = image_files[val_split:]

# Function to move files
def move_files(files, split):
    for file in files:
        shutil.move(f"{merged_image_dir}/{file}", f"{output_dir}/images/{split}/{file}")
        label_file = file.replace(".jpeg", ".txt").replace(".png", ".txt")
        if os.path.exists(f"{merged_label_dir}/{label_file}"):
            shutil.move(f"{merged_label_dir}/{label_file}", f"{output_dir}/labels/{split}/{label_file}")

# Move files to respective folders
move_files(train_files, "train")
move_files(val_files, "val")
move_files(test_files, "test")

print("Final dataset split complete!")
