import json
import os

root_path = "../carla_nus/dataset/nus/"

# Path to your JSON file
json_file_path = root_path + 'v1.0-trainval/lidarseg.json'

# Directory containing your segmentation files
lidarseg_dir_path = root_path + 'lidarseg/v1.0-trainval'

# Load the JSON data
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Extract the filenames of the used segmentation files from the JSON data
used_files = set()
for entry in data:
    # Extracting the filename only, not the entire path, assuming the filename is unique
    filename = os.path.basename(entry['filename'])
    used_files.add(filename)

# List all segmentation files in the lidarseg directory
all_files = {f for f in os.listdir(lidarseg_dir_path) if os.path.isfile(os.path.join(lidarseg_dir_path, f))}

# Identify unused files
unused_files = all_files - used_files

# Remove the unused files
for file in unused_files:
    os.remove(os.path.join(lidarseg_dir_path, file))
    print(f"Removed {file}")

print(f"Completed. Removed {len(unused_files)} unused files.")