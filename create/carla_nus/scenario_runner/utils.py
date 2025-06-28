__all__ = [
    "bbox_2d_from_agent",
    "calc_bbox2d_area",
    "calc_projected_2d_bbox",
    "check_occlusion",
    "degrees_to_radians",
    "depth_to_array",
    "distance_arrays",
    "draw_rect",
    "get_last_save_no",
    "get_relative_rotation_y",
    "inv",
    "midpoint_from_agent_location",
    "namedtuple",
    "point_in_canvas",
    "point_is_occluded",
    "proj_to_2d",
    "proj_to_camera",
    "relative_transform",
    "save_calibration_matrices",
    "save_groundplanes",
    "save_image_data",
    "save_kitti_data",
    "save_lidar_data",
    "save_lidar_data_sweeps",
    "save_lidarseg_tags",
    "save_ref_files",
    "to_bgra_array",
    "to_rgb_array",
    "transform_points",
    "transforms_from_agent",
    "vector3d_to_array",
    "vertex_to_world_vector",
    "vertex_vec3d_to_world_vector",
    "vertices_from_extension",
    "vertices_to_2d_coords",
    "create_directories",
    "array_to_location",
    "check_range",
]

import math
import toml

from collections import namedtuple

from pathlib import Path

import numpy as np

from numpy.linalg import inv

from constants import *

import carla

import cv2, re

Scale = namedtuple("Scale", "x y z")
Scale.__new__.__defaults__ = (1.0, 1.0, 1.0)

Translation = namedtuple("Translation", "x y z")
Translation.__new__.__defaults__ = (0.0, 0.0, 0.0)

Rotation = namedtuple("Rotation", "pitch yaw roll")
Rotation.__new__.__defaults__ = (0.0, 0.0, 0.0)


def depth_to_array(image):
    """
    Convert an image containing CARLA encoded depth-map to a 2D array containing
    the depth value of each pixel normalized between [0.0, 1.0].
    """
    array = to_bgra_array(image)
    array = array.astype(np.float32)
    # Apply (R + G * 256 + B * 256 * 256) / (256 * 256 * 256 - 1).
    normalized_depth = np.dot(array[:, :, :3], [65536.0, 256.0, 1.0])
    normalized_depth /= 16777215.0  # (256.0 * 256.0 * 256.0 - 1.0)
    return normalized_depth


def to_bgra_array(image):
    """Convert a CARLA raw image to a BGRA numpy array."""
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    return array


def check_occlusion(image, vertices_pos2d, depth_map, draw_vertices=True):
    """Draws each vertex in vertices_pos2d if it is in front of the camera
    The color is based on whether the object is occluded or not.
    Returns the number of visible vertices and the number of vertices outside the camera.
    """

    num_visible_vertices = 0
    num_vertices_outside_camera = 0


    for y_2d, x_2d, vertex_depth in vertices_pos2d:
        if MAX_RENDER_DEPTH_IN_METERS > vertex_depth > 0 and point_in_canvas(
            (y_2d, x_2d)
        ):
            is_occluded = point_is_occluded((y_2d, x_2d), vertex_depth, depth_map)
            if is_occluded:
                vertex_color = OCCLUDED_VERTEX_COLOR
            else:
                num_visible_vertices += 1
                vertex_color = VISIBLE_VERTEX_COLOR
        else:
            num_vertices_outside_camera += 1
    return num_visible_vertices, num_vertices_outside_camera


def check_range(vertices_pos2d):
    """
    Check the range from vertices
    """
    num_valid_vertices = 0
    num_invalid_vertices = 0

    for y_2d, x_2d, vertex_depth in vertices_pos2d:
        # if the point are not too far away
        if MAX_RENDER_DEPTH_IN_METERS > vertex_depth and -MAX_RENDER_DEPTH_IN_METERS < vertex_depth:
            # only care about the distance range, don't care about occlusion
            num_valid_vertices += 1
        else:
            num_invalid_vertices += 1
    return num_valid_vertices, num_invalid_vertices


def point_is_occluded(point, vertex_depth, depth_map):
    # def point_is_occluded(self, point, vertex_depth, depth_map):
    """Checks whether or not the four pixels directly around the given point has less depth than the given vertex depth
    If True, this means that the point is occluded.
    """
    y, x = map(int, point)

    from itertools import product

    neigbours = product((1, -1), repeat=2)

    is_occluded = []
    for dy, dx in neigbours:
        if point_in_canvas((dy + y, dx + x)):
            # If the depth map says the pixel is closer to the camera than the actual vertex
            if depth_map[y + dy, x + dx] < vertex_depth:
                is_occluded.append(True)
            else:
                is_occluded.append(False)
    # Only say point is occluded if all four neighbours are closer to camera than vertex
    return all(is_occluded)


def point_in_canvas(point):
    """Return true if point is in canvas"""
    # print(point[0], point[1])
    if (
        (point[0] >= 0)
        and (point[0] < WINDOW_HEIGHT)
        and (point[1] >= 0)
        and (point[1] < WINDOW_WIDTH)
    ):
        return True
    return False


def draw_rect(image, point, size, color=(255, 0, 255)):
    # def draw_rect(self, array, pos, size, color=(255, 0, 255)):
    """Draws a rect"""
    point_0 = (point[0] - size / 2, point[1] - size / 2)
    point_1 = (point[0] + size / 2, point[1] + size / 2)
    if point_in_canvas(point_0) and point_in_canvas(point_1):
        for i in range(size):
            for j in range(size):
                image[int(point_0[0] + i), int(point_0[1] + j)] = color


def vertices_from_extension(ext):
    """Extraxts the 8 bounding box vertices relative to (0,0,0)
    https://github.com/carla-simulator/carla/commits/master/Docs/img/vehicle_bounding_box.png
    8 bounding box vertices relative to (0,0,0)
    """
    return np.array(
        [
            [ext.x, ext.y, ext.z],  # Top left front
            [-ext.x, ext.y, ext.z],  # Top left back
            [ext.x, -ext.y, ext.z],  # Top right front
            [-ext.x, -ext.y, ext.z],  # Top right back
            [ext.x, ext.y, -ext.z],  # Bottom left front
            [-ext.x, ext.y, -ext.z],  # Bottom left back
            [ext.x, -ext.y, -ext.z],  # Bottom right front
            [-ext.x, -ext.y, -ext.z],  # Bottom right back
        ]
    )


def bbox_2d_from_agent(
    intrinsic_mat, extrinsic_mat, ext, bbox_transform, agent_transform, rotRP
):  # rotRP expects point to be in Kitti lidar format
    """Creates bounding boxes for a given agent and camera/world calibration matrices.
    Returns the modified image that contains the screen rendering with drawn on vertices from the agent"""
    bbox = vertices_from_extension(ext)
    # transform the vertices respect to the bounding box transform

    bbox = bbox_transform.transform_points(
        bbox
    )  

    # the bounding box transform is respect to the agents transform
    # so let's transform the points relative to it's transform

    bbox = agent_transform.transform_points(
        bbox
    )  

    # agents's transform is relative to the world, so now,
    # bbox contains the 3D bounding box vertices relative to the world
    # Additionally, you can logging.info these vertices to check that is working
    # Store each vertex 2d points for drawing bounding boxes later
    vertices_pos2d = vertices_to_2d_coords(bbox, intrinsic_mat, extrinsic_mat)

    return vertices_pos2d


def vertex_to_world_vector(vertex):
    """ Returns the coordinates of the vector in correct carla world format (X,Y,Z,1) """
    return np.array(
        [
            [vertex[0, 0]],  # [[X,
            [vertex[0, 1]],  # Y,
            [vertex[0, 2]],  # Z,
            [1.0],  # 1.0]]
        ]
    )


def vertex_vec3d_to_world_vector(vertex):
    """ Returns the coordinates of the vector in correct carla world format (X,Y,Z,1) """
    return np.array(
        [[vertex.x], [vertex.y], [vertex.z], [1.0]]  # [[X,  # Y,  # Z,  # 1.0]]
    )


def proj_to_camera(pos_vector, extrinsic_mat):
    # transform the points to camera

    transformed_3d_pos = np.dot(np.linalg.inv(extrinsic_mat), pos_vector)
    return transformed_3d_pos


def proj_to_2d(camera_pos_vector, intrinsic_mat):
    pos2d = camera_pos_vector

    pos2d = np.dot(intrinsic_mat, pos2d[:3])
    pos2d = np.array([pos2d[0] / pos2d[2], pos2d[1] / pos2d[2], pos2d[2]])
    # print(pos2d)
    return pos2d


def vertices_to_2d_coords(bbox, intrinsic_mat, extrinsic_mat):
    """Accepts a bbox which is a list of 3d world coordinates and returns a list
    of the 2d pixel coordinates of each vertex.
    This is represented as a tuple (y, x, d) where y and x are the 2d pixel coordinates
    while d is the depth. The depth can be used for filtering visible vertices.
    """
    vertices_pos2d = []
    for vertex in bbox:

        pos_vector = vertex_vec3d_to_world_vector(vertex)
        # Camera coordinates
        transformed_3d_pos = proj_to_camera(pos_vector, extrinsic_mat)
        # 2d pixel coordinates
        pos2d = proj_to_2d(transformed_3d_pos, intrinsic_mat)

        # The actual rendered depth (may be wall or other object instead of vertex)
        vertex_depth = pos2d[2]
        x_2d, y_2d = WINDOW_WIDTH - pos2d[0], WINDOW_HEIGHT - pos2d[1]
        vertices_pos2d.append((y_2d, x_2d, vertex_depth))
    return vertices_pos2d


def vector3d_to_array(vec3d):
    return np.array([vec3d.x, vec3d.y, vec3d.z])


def degrees_to_radians(degrees):
    return degrees * math.pi / 180


def distance_arrays(array1, array2):
    dx = array1[0] - array2[0]
    dy = array1[1] - array2[1]
    dz = array1[2] - array2[2]

    return np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)


def midpoint_from_agent_location(array, location, extrinsic_mat, intrinsic_mat):
    # Calculate the midpoint of the bottom chassis
    # This is used since kitti treats this point as the location of the car
    midpoint_vector = np.array(
        [[location.x], [location.y], [location.z], [1.0]]  # [[X,  # Y,  # Z,  # 1.0]]
    )
    transformed_3d_midpoint = proj_to_camera(midpoint_vector, extrinsic_mat)
    return transformed_3d_midpoint


def get_relative_rotation_y(agent_yaw, car_yaw):
    """Returns the relative rotation of the agent to the camera in yaw
    The relative rotation is the difference between the camera rotation (on car) and the agent rotation"""
    # We only car about the rotation for the classes we do detection on
    return degrees_to_radians(agent_yaw - car_yaw)


def relative_transform(source, target):
    source_t = source.get_inverse_matrix()
    transform_t = target.get_matrix()

    relative_transform_mat = np.dot(transform_t, source_t)
    return relative_transform_mat

    # loc = carla.Location(relative


def transform_points(point, transform_mat):
    return np.dot(transform_mat, point)


def calc_projected_2d_bbox(vertices_pos2d):
    """Takes in all vertices in pixel projection and calculates min and max of all x and y coordinates.
    Returns left top, right bottom pixel coordinates for the 2d bounding box as a list of four values.
    Note that vertices_pos2d contains a list of (y_pos2d, x_pos2d) tuples, or None
    """
    legal_pos2d = list(filter(lambda x: x is not None, vertices_pos2d))
    y_coords, x_coords = [int(x[0][0]) for x in legal_pos2d], [
        int(x[1][0]) for x in legal_pos2d
    ]
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    return [min_x, min_y, max_x, max_y]


def calc_bbox2d_area(bbox_2d):
    """Calculate the area of the given 2d bbox
    Input is assumed to be xmin, ymin, xmax, ymax tuple
    """
    xmin, ymin, xmax, ymax = bbox_2d
    return (ymax - ymin) * (xmax - xmin)


def transforms_from_agent(agent):
    """ Returns the KITTI object type and transforms, locations and extension of the given agent """
    if "pedestrian" in agent.type_id:
        obj_type = "pedestrian"
        agent_transform = agent.get_transform()  # Wrt world
        bbox_transform = (carla.Transform(
            agent.bounding_box.location, agent.bounding_box.rotation
        ), carla.AttachmentType.Rigid)  # Wrt Agent
        ext = agent.bounding_box.extent
        location = agent.get_location()

    elif "vehicle" in agent.type_id:
        if ("diamondback.century" in agent.type_id
                or "bh.crossbike" in agent.type_id
                or "gazelle.omafiets" in agent.type_id):
            obj_type = "bicycle"
            agent_transform = agent.get_transform()
            bbox_transform = (carla.Transform(
                agent.bounding_box.location, agent.bounding_box.rotation
            ), carla.AttachmentType.Rigid)
            ext = agent.bounding_box.extent
            location = agent.get_location()

        elif ("harley-davidson.low_rider" in agent.type_id
              or "kawasaki.ninja" in agent.type_id
              or "vespa.zx125" in agent.type_id
              or "yamaha.yzf" in agent.type_id):
            obj_type = "motorcycle"
            agent_transform = agent.get_transform()
            bbox_transform = (carla.Transform(
                agent.bounding_box.location, agent.bounding_box.rotation
            ), carla.AttachmentType.Rigid)
            ext = agent.bounding_box.extent
            location = agent.get_location()

        elif ("mitsubishi.fusorosa" in agent.type_id
              or "volkswagen.t2_2021" in agent.type_id
              or "volkswagen.t2" in agent.type_id
              or "mercedes.sprinter" in agent.type_id
              or "ford.ambulance" in agent.type_id):
            obj_type = "bus"
            agent_transform = agent.get_transform()
            bbox_transform = (carla.Transform(
                agent.bounding_box.location, agent.bounding_box.rotation
            ), carla.AttachmentType.Rigid)
            ext = agent.bounding_box.extent
            location = agent.get_location()

        elif ("tesla.cybertruck" in agent.type_id
              or "carlamotors.firetruck" in agent.type_id
              or "carlamotors.european_hgv" in agent.type_id
              or "carlamotors.carlacola" in agent.type_id):
            obj_type = "truck"
            agent_transform = agent.get_transform()
            bbox_transform = (carla.Transform(
                agent.bounding_box.location, agent.bounding_box.rotation
            ), carla.AttachmentType.Rigid)
            ext = agent.bounding_box.extent
            location = agent.get_location()

        else:
            obj_type = "car"
            agent_transform = agent.get_transform()
            bbox_transform = (carla.Transform(
                agent.bounding_box.location, agent.bounding_box.rotation
            ), carla.AttachmentType.Rigid)
            ext = agent.bounding_box.extent
            location = agent.get_location()

    else:
        return (None, None, None, None, None)
    return obj_type, agent_transform, bbox_transform, ext, location


def to_rgb_array(image):
    """Convert a CARLA raw image to a RGB numpy array."""
    array = to_bgra_array(image)
    # Convert BGRA to RGB.
    array = array[:, :, :3]
    array = array[:, :, ::-1]
    return array


import cv2
import numpy as np
import os


def save_groundplanes(planes_fname, transform, lidar_height):
    from math import cos, sin

    """ Saves the groundplane vector of the current frame.
        The format of the ground plane file is first three lines describing the file (number of parameters).
        The next line is the three parameters of the normal vector, and the last is the height of the normal vector,
        which is the same as the distance to the camera in meters.
    """
    rotation = transform.rotation
    pitch, roll = rotation.pitch, rotation.roll
    # Since measurements are in degrees, convert to radians
    pitch = degrees_to_radians(pitch)
    roll = degrees_to_radians(roll)
    # Rotate normal vector (y) wrt. pitch and yaw
    normal_vector = [cos(pitch) * sin(roll), -cos(pitch) * cos(roll), sin(pitch)]
    normal_vector = map(str, normal_vector)
    with open(planes_fname, "w") as f:
        f.write("# Plane\n")
        f.write("Width 4\n")
        f.write("Height 1\n")
        f.write("{} {}\n".format(" ".join(normal_vector), lidar_height))


def save_ref_files(folder, id):
    """ Appends the id of the given record to the files """
    # NO USE
    # for name in ["train.txt", "val.txt", "trainval.txt"]:
    for name in ["logs/data_index_list.txt"]:
        path = os.path.join(folder, name)
        with open(path, "a") as f:
            f.write("15{0:014}".format(id) + "\n")


def save_image_data(filename, image):
    # Convert to correct color format
    color_fmt = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, color_fmt)
    print(f"Saving {filename}")


def save_lidar_data(filename, point_cloud, LIDAR_HEIGHT, format):
    """Saves lidar data to given filename, according to the lidar data format.
    bin is used for KITTI-data format, while .ply is the regular point cloud format
    In Unreal, the coordinate system of the engine is defined as, which is the same as the lidar points
    z
    ^   ^ x
    |  /
    | /
    |/____> y
    This is a left-handed coordinate system, with x being forward, y to the right and z up
    See also https://github.com/carla-simulator/carla/issues/498
    However, the lidar coordinate system from KITTI is defined as
          z
          ^   ^ x
          |  /
          | /
    y<____|/
    Which is a right handed coordinate sylstem
    Therefore, we need to flip the y axis of the lidar in order to get the correct lidar format for kitti.

    This corresponds to the following changes from Carla to Kitti
        Carla: X   Y   Z
        KITTI: X  -Y   Z
    NOTE: We do not flip the coordinate system when saving to .ply.
    """

    if format == "bin":

        # fov_down = -25 / 180.0 * np.pi
        # fov = (abs(-25) + abs(5.0)) / 180.0 * np.pi
        # proj_y = (pitch + abs(fov_down)) / fov  # in [0.0, 1.0]
        # proj_y *= 64  # in [0.0, H]
        # proj_y = np.floor(proj_y)
        # proj_y = np.minimum(64 - 1, proj_y)
        # proj_y = np.maximum(0, proj_y).astype(np.int32)  # in [0,H-1]
        # proj_y = proj_y.reshape(-1, 1)

        lidar_array = [[point[1], point[0], point[2], 1.0, 0] for point in point_cloud]
        lidar_array = np.array(lidar_array).astype(np.float32)
        lidar_array.tofile(filename)
    elif format == "pcd":
        lidar_array = [[point[1], point[0], point[2], 1.0, 0] for point in point_cloud]
        lidar_array = np.array(lidar_array).astype(np.float32)
        lidar_array.tofile(filename)
    else:
        raise ValueError
    print(f"Saving {filename}")


def save_lidar_data_sweeps(filename, point_cloud, LIDAR_HEIGHT, format):
    """Saves lidar data to given filename, according to the lidar data format.
    bin is used for KITTI-data format, while .ply is the regular point cloud format
    In Unreal, the coordinate system of the engine is defined as, which is the same as the lidar points
    z
    ^   ^ x
    |  /
    | /
    |/____> y
    This is a left-handed coordinate system, with x being forward, y to the right and z up
    See also https://github.com/carla-simulator/carla/issues/498
    However, the lidar coordinate system from KITTI is defined as
          z
          ^   ^ x
          |  /
          | /
    y<____|/
    Which is a right handed coordinate sylstem
    Therefore, we need to flip the y axis of the lidar in order to get the correct lidar format for kitti.

    This corresponds to the following changes from Carla to Kitti
        Carla: X   Y   Z
        KITTI: X  -Y   Z
    NOTE: We do not flip the coordinate system when saving to .ply.
    """

    if format == "bin":

        # fov_down = -25 / 180.0 * np.pi
        # fov = (abs(-25) + abs(5.0)) / 180.0 * np.pi
        # proj_y = (pitch + abs(fov_down)) / fov  # in [0.0, 1.0]
        # proj_y *= 64  # in [0.0, H]
        # proj_y = np.floor(proj_y)
        # proj_y = np.minimum(64 - 1, proj_y)
        # proj_y = np.maximum(0, proj_y).astype(np.int32)  # in [0,H-1]
        # proj_y = proj_y.reshape(-1, 1)

        lidar_array = [[point[1], point[0], point[2], 1.0, 0] for point in point_cloud]
        lidar_array = np.array(lidar_array).astype(np.float32)
        lidar_array.tofile(filename)
    elif format == "pcd":
        lidar_array = [[point[1], point[0], point[2], 1.0, 0] for point in point_cloud]
        lidar_array = np.array(lidar_array).astype(np.float32)
        lidar_array.tofile(filename)
    else:
        raise ValueError

def save_lidarseg_tags(filename, lidar_tags, format):
    """Saves lidar data to given filename, according to the lidar data format.
    bin is used for NuScenes-data format, while .ply is the regular point cloud format
    In Unreal, the coordinate system of the engine is defined as, which is the same as the lidar points
    z
    ^   ^ x
    |  /
    | /
    |/____> y
    This is a left-handed coordinate system, with x being forward, y to the right and z up
    See also https://github.com/carla-simulator/carla/issues/498

    """

    if format == "bin":
        lidarseg_array = np.array(lidar_tags).astype(np.uint8)
        lidarseg_array.tofile(filename)
    else:
        raise ValueError
    print(f"Saving {filename}")


def save_kitti_data(filename, datapoints):
    with open(filename, "w") as f:
        out_str = "\n".join([str(point) for point in datapoints if point])
        f.write(out_str)


def save_calibration_matrices(filename, intrinsic_mat, extrinsic_mat):
    """Saves the calibration matrices to a file.
    AVOD (and KITTI) refers to P as P=K*[R;t], so we will just store P.
    The resulting file will contain:
    3x4    p0-p3      Camera P matrix. Contains extrinsic
                      and intrinsic parameters. (P=K*[R;t])
    3x3    r0_rect    Rectification matrix, required to transform points
                      from velodyne to camera coordinate frame.
    3x4    tr_velodyne_to_cam    Used to transform from velodyne to cam
                                 coordinate frame according to:
                                 Point_Camera = P_cam * R0_rect *
                                                Tr_velo_to_cam *
                                                Point_Velodyne.
    3x4    tr_imu_to_velo        Used to transform from imu to velodyne coordinate frame. This is not needed since we do not export
                                 imu data.
    """
    # KITTI format demands that we flatten in row-major order
    ravel_mode = "C"
    # easy_extrinsic = np.array([[1, 0, 0, 0], [0, 1, 0, -CAMERA_HEIGHT_POS/2], [0, 0, 1, 0]])
    easy_extrinsic = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]])
    P0 = np.dot(intrinsic_mat, easy_extrinsic)
    assert P0.shape == (3, 4)
    P0 = np.ravel(P0, order=ravel_mode)
    R0 = np.identity(3)
    TR_velodyne = np.array([[0, -1, 0], [0, 0, -1], [1, 0, 0]])
    # Add translation vector from velo to camera. This is 0 because the position of camera and lidar is equal in our configuration.
    TR_velodyne = np.column_stack((TR_velodyne, np.array([0, 0, 0])))
    TR_imu_to_velo = np.identity(3)
    TR_imu_to_velo = np.column_stack((TR_imu_to_velo, np.array([0, 0, 0])))

    def write_flat(f, name, arr):
        f.write(
            "{}: {}\n".format(
                name, " ".join(map(str, arr.flatten(ravel_mode).squeeze()))
            )
        )

    # All matrices are written on a line with spacing
    with open(filename, "w") as f:
        for i in range(
            4
        ):  # Avod expects all 4 P-matrices even though we only use the first
            write_flat(f, "P" + str(i), P0)
        write_flat(f, "R0_rect", R0)
        write_flat(f, "Tr_velo_to_cam", TR_velodyne)
        write_flat(f, "TR_imu_to_velo", TR_imu_to_velo)


def get_last_save_no(self, split):

    path = Path(self.OUTPUT_FOLDER) / split
    path_label = path / "calib"

    path_label_0 = path_label / "000100000001.txt"  # 000001.txt
    if not path_label_0.exists():
        return 0

    files = list(path_label.glob("*"))

    nums = []
    for file in files:

        nums.append(int(re.findall("\d+", str(file.name))[0].lstrip("0")))

    num = max(nums)
    return num


def create_directories(self, split, args):
    path = Path(self.OUTPUT_FOLDER)
    os.makedirs(path / "logs", exist_ok=True)

    os.makedirs(path / "IMAGE/CAM_FRONT", exist_ok=True)
    os.makedirs(path / "IMAGE/CAM_FRONT_LEFT", exist_ok=True)
    os.makedirs(path / "IMAGE/CAM_FRONT_RIGHT", exist_ok=True)
    os.makedirs(path / "IMAGE/CAM_BACK", exist_ok=True)
    os.makedirs(path / "IMAGE/CAM_BACK_LEFT", exist_ok=True)
    os.makedirs(path / "IMAGE/CAM_BACK_RIGHT", exist_ok=True)

    ldv = toml.load(f"../hyperparams/{args.lidar_params}")['lidar']
    cdv = toml.load(f"../hyperparams/{args.lidar_params}")['camera']

    print(ldv)
    print(cdv)
    
    for p in range(ldv["sets"]):
        os.makedirs(path / f"LiDAR_p{p}_samples/samples/LIDAR_TOP", exist_ok=True)
        os.makedirs(path / f"LiDAR_p{p}_samples/sweeps/LIDAR_TOP", exist_ok=True)
        os.makedirs(path / f"LiDAR_p{p}_samples/lidarseg/v1.0-trainval", exist_ok=True)
        os.makedirs(path / f"LiDAR_p{p}_samples/sweeps_lidarseg/v1.0-trainval", exist_ok=True)

    path = Path(self.OUTPUT_FOLDER) / split
    os.makedirs(path / "label_2", exist_ok=True)
    os.makedirs(path / "image_2", exist_ok=True)
    os.makedirs(path / "position", exist_ok=True)
    os.makedirs(path / "timestamp", exist_ok=True)
    os.makedirs(path / "velodyne", exist_ok=True)
    os.makedirs(path / "calib", exist_ok=True)
    os.makedirs(path / "planes", exist_ok=True)


def array_to_location(array: np.ndarray):
    locations = []
    for i in range(array.shape[0]):
        locations.append(carla.Location(array[i, 0], array[i, 1], array[i, 2]))

    return locations
