# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import numpy as np
import open3d as o3d
import os
from tqdm import tqdm
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


def open_read_txt(file_name):
    data = []
    file = open(file_name, 'r')
    file_data = file.readlines()
    for row in file_data:
        tmp_list = row.split(' ')
        data.append(tmp_list)
    return data


def read_point_cloud_bin(file_path):
    with open(file_path, 'rb') as f:
        # Read and parse binary point cloud file
        pc_data = np.fromfile(f, dtype=np.float32)
        # Reshape according to the format (N, 4) - x, y, z, reflectance
        pc_data = pc_data.reshape(-1, 5)
        points = pc_data[:, :3]  # We only need x, y, z

    return points


def parse_line(line):
    parts = line.strip().split(' ')
    obj_type = parts[0]
    truncated = float(parts[1])
    occluded = int(parts[2])
    alpha = float(parts[3])
    bbox_2d = list(map(int, parts[4:8]))
    dimensions = list(map(float, parts[8:11]))  # height, width, length
    location = list(map(float, parts[11:14]))  # x, y, z
    rotation_yaw = float(parts[14])
    instance_id = int(parts[15])
    speed = float(parts[-1])

    return {
        'type': obj_type,
        'truncated': truncated,
        'occluded': occluded,
        'alpha': alpha,
        'bbox_2d': bbox_2d,
        'dimensions': dimensions,
        'location': location,
        'rotation_yaw': rotation_yaw,
        'instance_id': instance_id,
        'speed': speed
    }


def save_valid_bboxes(valid_objects, output_file_path):
    valid_bboxes = []
    with open(output_file_path, 'w') as file:
        for obj in valid_objects:
            line = f"{obj['type']} {obj['truncated']} {obj['occluded']} {obj['alpha']} " \
                   f"{obj['bbox_2d'][0]} {obj['bbox_2d'][1]} {obj['bbox_2d'][2]} {obj['bbox_2d'][3]} " \
                   f"{obj['dimensions'][0]} {obj['dimensions'][1]} {obj['dimensions'][2]} " \
                   f"{obj['location'][0]} {obj['location'][1]} {obj['location'][2]} " \
                   f"{obj['rotation_yaw']} {obj['instance_id']} {obj['speed']}\n"
            file.write(line)
            valid_bbox = create_bbox(obj)
            valid_bboxes.append(valid_bbox)

    return valid_bboxes


def create_bbox(obj):
    h, w, l = obj['dimensions']
    cam_x, cam_y, cam_z = obj['location']
    cam_yaw = obj['rotation_yaw']

    x, y, z = cam_x, cam_z, -cam_y+h/2
    yaw = -cam_yaw

    bbox = o3d.geometry.OrientedBoundingBox(
        center=(x, y, z),
        R=o3d.geometry.OrientedBoundingBox.get_rotation_matrix_from_xyz((0, 0, yaw)),
        extent=(l, w, h)  # chang, kuan, gao
    )
    bbox.color = [0, 1, 0.6]

    return bbox


def load_point_cloud(bin_path):
    point_cloud = np.fromfile(bin_path, dtype=np.float32).reshape(-1, 5)[:, :3]
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)
    pcd.paint_uniform_color([0, 0, 1])

    # Compute depth as the Euclidean distance in the xy-plane
    # xy_depth = np.linalg.norm(point_cloud[:, :2], axis=1)
    # depth_min = xy_depth.min()
    # depth_max = xy_depth.max()
    # depth_norm = 1- (xy_depth / (depth_max - depth_min)) # Normalize depth values to range [0, 1]
    # colormap = plt.get_cmap('viridis')  # Choose a colormap
    # colors = colormap(depth_norm)[:, :3]  # Apply colormap and take RGB channels
    # Map depth to blue color intensity
    # colors = np.zeros((point_cloud.shape[0], 3))
    # colors[:, 2] = depth_norm  # Set blue channel intensity based on normalized depth
    # pcd.colors = o3d.utility.Vector3dVector(colors)

    return pcd


def process_files(txt_folder, pcd_folder, output_folder, label_index_path):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # txt_files = []
    # bin_files = []
    #
    # label_indexs = open_read_txt(label_index_path)
    # for index in label_indexs:
    #     txt_files.append(index[0] + '.txt')

    txt_files = [f for f in os.listdir(txt_folder) if f.endswith('.txt')]
    bin_files = [f for f in os.listdir(pcd_folder) if f.endswith('.pcd.bin')]

    vis = o3d.visualization.Visualizer()
    vis.create_window()
    opt = vis.get_render_option()
    opt.background_color = np.asarray([0, 0, 0])

    for txt_file in tqdm(txt_files):
        identifier = txt_file.split('.')[0]
        bin_file = f'n008-2018-08-01-00-00-00-0400__LIDAR_TOP__{identifier}.pcd.bin'
        if bin_file not in bin_files:
            print(f'{bin_file} not found!')
            continue

        txt_file_path = os.path.join(txt_folder, txt_file)
        bin_file_path = os.path.join(pcd_folder, bin_file)
        output_file_path = os.path.join(output_folder, txt_file)

        pcd, valid_bboxes = pre_render(txt_file_path, bin_file_path, output_file_path)

        # Clear previous geometries
        vis.clear_geometries()

        # Add new geometries to the visualizer
        vis.add_geometry(pcd)
        for bbox in valid_bboxes:
            vis.add_geometry(bbox)

        vis.poll_events()
        vis.update_renderer()

    vis.destroy_window()


def pre_render(txt_file_path, bin_file_path, output_file_path):
    pcd = load_point_cloud(bin_file_path)

    with open(txt_file_path, 'r') as file:
        lines = file.readlines()

    objects = [parse_line(line) for line in lines]

    bboxes = []
    point_counts = []
    valid_objects = []
    for obj in objects:
        bbox = create_bbox(obj)
        bboxes.append(bbox)
        cropped_pcd = pcd.crop(bbox)
        point_count = len(cropped_pcd.points)
        point_counts.append(point_count)
        if point_count > 5:
            valid_objects.append(obj)
        elif point_count > 3 and obj['type'] in ['pedestrian', 'bicycle', 'motorcycle']:
            valid_objects.append(obj)
    # for i, count in enumerate(point_counts):
    #     print(f"Bounding Box {i + 1} contains {count} points")

    _valid_bboxes = save_valid_bboxes(valid_objects, output_file_path)

    return pcd, _valid_bboxes


def run(pcd, bboxes):
    vis = o3d.visualization.Visualizer()
    vis.create_window()

    opt = vis.get_render_option()
    opt.background_color = np.asarray([0, 0, 0])

    vis.add_geometry(pcd)
    for bbox in bboxes:
        vis.add_geometry(bbox)

    vis.run()
    vis.destroy_window()


if __name__ == '__main__':
    set_cpu_affinity('Efficient')

    pcd_folder = '../carla_nus/dataset/nus/LiDAR_p0_samples/samples/LIDAR_TOP'
    txt_folder = '../carla_nus/dataset/nus/training/label_2'
    output_folder = '../carla_nus/dataset/nus/training/refine_2/'
    label_index_path = '../carla_nus/dataset/nus/logs/data_index_list.txt'

    process_files(txt_folder, pcd_folder, output_folder, label_index_path)

    print('Successfully rendering all labels!')

