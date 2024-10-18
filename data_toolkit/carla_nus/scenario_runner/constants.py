import os
import numpy as np

CAMERA_IMAGE_X = 1600
CAMERA_IMAGE_Y = 900

WINDOW_WIDTH = CAMERA_IMAGE_X
WINDOW_HEIGHT = CAMERA_IMAGE_Y

#################################################

SAVE_DISTANCE = 2
SAVE_INTERVAL = 0.48

MAX_RENDER_DEPTH_IN_METERS = 70.0
MIN_VISIBLE_VERTICES_FOR_RENDER = 4

MIN_VALID_VERTICES_FOR_RENDER = 4
MAX_INVALID_VERTICES_FOR_RENDER = 4

LIMITS = np.array(
    [
        [-66.7, 66.7],
        [-66.7, 66.7],
        [-3.0, 1.0]
    ]
)

MAX_LIMIT = np.array(
    [
        [-66.7, 66.7],
        [-66.7, 66.7],
        [-3.0, 1.0]
    ]
)

# LIMITS = np.array(
#     [
#         [-40.0, 40.0],
#         [-20.0, 20.0],
#         [-3.0, 1.0]
#     ]
# )
#
# MAX_LIMIT = np.array(
#     [
#         [-40.0, 40.0],
#         [-20.0, 20.0],
#         [-3.0, 1.0]
#     ]
# )

MIN_BBOX_AREA_IN_PX = 100

OCCLUDED_VERTEX_COLOR = (255, 0, 0)
VISIBLE_VERTEX_COLOR = (0, 255, 0)

WINDOW_WIDTH_HALF = WINDOW_WIDTH / 2
WINDOW_HEIGHT_HALF = WINDOW_HEIGHT / 2

CLASSES_TO_LABEL = ["Vehicle", "Pedestrian"]

# Save Paths
""" OUTPUT FOLDER GENERATION """

# ignore all the things below
OUTPUT_FOLDER = "XXX/dataset"

""" DATA SAVE PATHS """
# GROUNDPLANE_PATH = os.path.join(OUTPUT_FOLDER, 'training/planes/{0:06}.txt')
# LIDAR_PATH = os.path.join(OUTPUT_FOLDER, 'training/velodyne/{0:06}.bin')
# LIDAR_BEAM_PATH = os.path.join(OUTPUT_FOLDER, 'training/velodyne/{0:06}_{2}.bin')
# LABEL_PATH = os.path.join(OUTPUT_FOLDER, 'training/label_2/{0:06}.txt')
# IMAGE_PATH = os.path.join(OUTPUT_FOLDER, 'training/image_2/{0:06}.jpg')
# CALIBRATION_PATH = os.path.join(OUTPUT_FOLDER, 'training/calib/{0:06}.txt')










