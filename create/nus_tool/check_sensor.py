# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import json
import os
import psutil
import time


# Function to set CPU affinity
def set_cpu_affinity(mode):
    cpu_cores = []
    total_cpus = 16
    used_cpus = None
    start = int(time.time()) % total_cpus

    if mode == 'Efficient':
        used_cpus = 2
    elif mode == 'Performance':
        used_cpus = 4
    else:
        print(f'Error {mode}!')

    for _ in range(used_cpus):
        cpu_cores.append(start)
        start += 2
        if start >= total_cpus:
            start -= total_cpus

    p = psutil.Process(os.getpid())
    p.cpu_affinity(cpu_cores)

    print(f"Process is set to use CPU cores: {cpu_cores}")


def run():

    root_path = "../carla_nus/dataset/nus/LIDAR_p0_samples/"

    # Path to your JSON file
    json_file_path = root_path + 'v1.0-trainval/sample_data.json'

    # Directory containing your segmentation files
    samples_dir_path = root_path + 'samples/'
    sweeps_dir_path = root_path + 'sweeps/'

    # Load the JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Extract the filenames of the used segmentation files from the JSON data
    used_files = set()
    for entry in data:
        # Extracting the filename only, not the entire path, assuming the filename is unique
        # filename = os.path.basename(entry['filename'])
        used_files.add(entry['filename'])

    all_files = set()
    # List each item in the given directory
    for item in os.listdir(samples_dir_path):
        # Create full path to item
        path = os.path.join(samples_dir_path, item)
        # Check if this item is a directory
        if os.path.isdir(path):
            # List all files in this sub-directory
            for f in os.listdir(path):
                all_files.add(os.path.join('samples', item, f))  # Add these files to the list

    # for item in os.listdir(sweeps_dir_path):
    #     # Create full path to item
    #     path = os.path.join(sweeps_dir_path, item)
    #     # Check if this item is a directory
    #     if os.path.isdir(path):
    #         # List all files in this sub-directory
    #         for f in os.listdir(path):
    #             all_files.add(os.path.join('sweeps', item, f))  # Add these files to the list

    # Identify unused files
    unused_files = all_files - used_files

    # Remove the unused files
    for file in unused_files:
        os.remove(os.path.join(root_path, file))
        # print(f"Removed {os.path.join(root_path, file)}")

    print(f"Completed. Removed {len(unused_files)} unused files.")


if __name__ == '__main__':
    set_cpu_affinity('Efficient')
    run()

    print('Done!')



