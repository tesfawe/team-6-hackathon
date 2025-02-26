import os
import json
import shutil

def load_json_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def upload_csv(remote_config_path, local_csv_path):
    # Load remote configuration from JSON
    config = load_json_config(remote_config_path)
    remote_dir = config.get("remote_directory")
    warehouse_name = config.get("warehouse_name")

    # Validate that the remote directory and warehouse name exist in config
    if not remote_dir or not warehouse_name:
        raise ValueError("Both 'remote_directory' and 'warehouse_name' must be specified in the configuration.")

    # Construct the destination file path (renamed to the warehouse name)
    dest_file = os.path.join(remote_dir, f"{warehouse_name}.csv")

    # Copy the local CSV file to the remote directory with the new name
    shutil.copy(local_csv_path, dest_file)
    print(f"Uploaded '{local_csv_path}' to '{dest_file}' successfully.")

if __name__ == "__main__":
    remote_config_path = "configs/remote_dir_config.json"
    local_csv_path = "data/stacks.csv"
    upload_csv(remote_config_path, local_csv_path)
