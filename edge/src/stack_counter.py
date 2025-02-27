from datetime import datetime

import cv2
import time
import os
import random
from collections import Counter


def count_boxes(image):
    """
    Placeholder function to count the number of boxes in an image.
    To be implemented later.

    For now, we simulate by returning a random integer between 0 and 10.
    """
    return random.randint(0, 10)


def capture_image():
    """
    Captures an image from the default camera.
    In a real application, this would interface with the actual hardware.
    """
    cap = cv2.VideoCapture(0)  # Use device 0 (default camera)
    if not cap.isOpened():
        print("Camera could not be opened.")
        return None

    ret, frame = cap.read()
    cap.release()

    if ret:
        return frame
    else:
        print("Failed to capture image.")
        return None


def majority_vote(counts) -> int:
    """
    Returns the mode (most common value) from the list of counts.
    If there is a tie, returns one of the most common counts.
    """
    if not counts:
        return 0
    vote = Counter(counts)
    return int(vote.most_common(1)[0][0])


def main():
    # Every INTERVAL seconds, take a batch of pictures with the camera
    INTERVAL = 5
    # The number of pictures to take in one batch
    NUM_PICS = 5
    # The number of boxes in the stack to be problematic:
    SAFE_THRESHOLD = 5
    # Camera ID
    camera_id = 1
    # The warehouse or central computer storage path
    warehouse_cpu_photo_storage_path = "../data"

    # Create directories if they don't exist
    os.makedirs(warehouse_cpu_photo_storage_path, exist_ok=True)

    last_max_count = 0
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"\n--- Batch {timestamp}: Capturing {NUM_PICS} pictures ---")
        images = []
        counts = []

        # Capture NUM_PICS images in quick succession
        for i in range(NUM_PICS):
            print(f"Capturing picture {i + 1}/{NUM_PICS} at {timestamp}...")
            img = capture_image()
            if img is not None:
                images.append(img)
                box_count = count_boxes(img)
                counts.append(box_count)
                print(f"Picture {i + 1} predicted box count: {box_count}")
            else:
                print(f"Picture {i + 1} was not captured properly.")

            # (Optional) Small delay between captures within a batch, if needed
            time.sleep(0.1)

        if not counts:
            print("No valid images captured in this batch. Skipping evaluation.")
        else:
            majority_count = majority_vote(counts)
            print(f"Majority vote box count for batch {timestamp}: {majority_count}")
            # Save the first image from the batch if majority vote is > SAFE_THRESHOLD
            if majority_count > SAFE_THRESHOLD and majority_count == last_max_count:
                camera_remote_file_store_path = os.path.join(warehouse_cpu_photo_storage_path, f"camera{camera_id}")
                os.makedirs(camera_remote_file_store_path, exist_ok=True)
                filename = os.path.join(camera_remote_file_store_path, f"batch_{timestamp}_image_0.jpg")
                cv2.imwrite(filename, images[0])
                text_filename = os.path.join(camera_remote_file_store_path, f"batch_{timestamp}_image_0.txt")
                with open(text_filename, 'w') as f:
                    f.write(f"{camera_id},{timestamp}, {majority_count}")
                print(f"Saved image '{filename}' (majority count > 5).")
            else:
                print("Batch discarded (majority count <= 5 or the situation was already reported).")
            last_max_count = majority_count
            # Wait for the specified interval before starting the next batch
            print(f"Waiting {INTERVAL} seconds before next batch...\n")
            time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
