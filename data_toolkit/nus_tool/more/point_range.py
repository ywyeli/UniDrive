# import os
# import numpy as np
#
# def get_max_min_points_from_bin(folder_path):
#     max_points = np.array([float('-inf'), float('-inf'), float('-inf')])
#     min_points = np.array([float('inf'), float('inf'), float('inf')])
#
#     for filename in os.listdir(folder_path):
#         if filename.endswith('.bin'):
#             file_path = os.path.join(folder_path, filename)
#             # Assuming each point is [x, y, z, reflectance]
#             points = np.fromfile(file_path, dtype=np.float32).reshape(-1, 5)
#             max_points = np.maximum(max_points, np.max(points[:, :3], axis=0))
#             min_points = np.minimum(min_points, np.min(points[:, :3], axis=0))
#
#     return max_points, min_points
#

# max_points, min_points = get_max_min_points_from_bin(folder_path)
#
# print(f"Maximum values for X, Y, Z are: {max_points}")
# print(f"Minimum values for X, Y, Z are: {min_points}")

import os
import numpy as np

def get_extreme_points_from_bin(folder_path):
    max_points = np.array([float('-inf'), float('-inf'), float('-inf')])
    min_points = np.array([float('inf'), float('inf'), float('inf')])
    max_points_files = ["", "", ""]
    min_points_files = ["", "", ""]

    for filename in os.listdir(folder_path):
        if filename.endswith('.bin'):
            file_path = os.path.join(folder_path, filename)
            # Assuming each point is [x, y, z, reflectance]
            points = np.fromfile(file_path, dtype=np.float32).reshape(-1, 5)
            current_max = np.max(points[:, :3], axis=0)
            current_min = np.min(points[:, :3], axis=0)

            for i in range(3):
                if current_max[i] > max_points[i]:
                    max_points[i] = current_max[i]
                    max_points_files[i] = filename
                if current_min[i] < min_points[i]:
                    min_points[i] = current_min[i]
                    min_points_files[i] = filename

    return max_points, min_points, max_points_files, min_points_files

folder_path = '/home/.../Documents/Dataset_line/samples0/LIDAR_TOP'
max_points, min_points, max_points_files, min_points_files = get_extreme_points_from_bin(folder_path)

print(f"Maximum values for X, Y, Z are: {max_points}, in files: {max_points_files}")
print(f"Minimum values for X, Y, Z are: {min_points}, in files: {min_points_files}")






# folder_path = '/home/../Documents/Dataset_line/samples0/LIDAR_TOP'
#
# ranges = get_point_ranges_from_bin(folder_path)
# print(f"Maximum ranges for X, Y, Z are: {ranges}")