import argparse
import os

from utils import draw_yolo, get_input_data, get_plain_bboxes_list

CLASSES = [0,1]

def draw(image_file):
    print(image_file)
    path = os.path.normpath(image_file)
    parts = path.split(os.sep)
    #parts = os.path.split(image_file)
    print("Parts:", parts)
    
    folder_path = os.path.join(*parts[:-2])
    image_file = parts[-1]
    label_path = os.path.splitext(parts[-1])[0] + ".txt"

    labels = get_plain_bboxes_list(f"{folder_path}/labels/{label_path}", CLASSES)
    image, _, _ = get_input_data(folder_path, image_file)
    
    draw_yolo(folder_path, image, labels)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Augment images.")
    parser.add_argument("--image_path", type=str, help="Path to the source image")

    args = parser.parse_args()
    draw(args.image_path)