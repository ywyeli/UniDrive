# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import os
import json
from math import pi, sin, cos, atan, sqrt
import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def points_to_convex_polygon(points):
    hull = ConvexHull(points)
    hull_points = points[hull.vertices]
    return Polygon(hull_points)

# open label folder
def openreadtxt(file_name):
    data = []
    file = open(file_name, 'r')
    file_data = file.readlines()
    for row in file_data:
        tmp_list = row.split(' ')
        data.append(tmp_list)
    return data


def create_sensor_json(sensor_json, sensor_list):
    create_sensor_token = None
    for s in sensor_list:
        if s == 'LIDAR_TOP':
            modality = 'lidar'
            create_sensor_token = 'lidartoplidartoplidartoplidartop'
        else:
            modality = 'camera'
            if s == 'CAM_FRONT':
                create_sensor_token = 'camfrontcamfrontcamfrontcamfront'
            if s == 'CAM_BACK':
                create_sensor_token = 'cambackcambackcambackcambackcamb'
            if s == 'CAM_FRONT_LEFT':
                create_sensor_token = 'camfrontleftcamfrontleftcamfront'
            if s == 'CAM_FRONT_RIGHT':
                create_sensor_token = 'camfrontrightcamfrontrightcamfro'
            if s == 'CAM_BACK_LEFT':
                create_sensor_token = 'cambackleftcambackleftcambacklef'
            if s == 'CAM_BACK_RIGHT':
                create_sensor_token = 'cambackrightcambackrightcambackr'
        sensor_json.append(
            {'token': create_sensor_token,
             'channel': s,
             'modality': modality}
        )
    sensor_jsondata = json.dumps(sensor_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/sensor.json', 'w')
    f.write(sensor_jsondata)
    f.close()


def create_visibility_json(visibility_json):
    visibility_json.append(
        {'description': 'visibility of whole object is between 80 and 100%',
         'token': '4',
         'level': 'v80-100'}
    )
    visibility_json.append(
                {'description': 'visibility of whole object is between 60 and 80%',
             'token': '3',
             'level': 'v60-80'}
    )
    visibility_json.append(
                {'description': 'visibility of whole object is between 40 and 60%',
             'token': '2',
             'level': 'v40-60'}
    )
    visibility_json.append(
                {'description': 'visibility of whole object is between 20 and 40%',
             'token': '1',
             'level': 'v20-40'}
    )
    visibility_jsondata = json.dumps(visibility_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/visibility.json', 'w')
    f.write(visibility_jsondata)
    f.close()


def create_lidarseg_category_json(lidarseg_category_json):
    create_category_token = 'categorylidarsegcategory00000000'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'None',
         'description': 'None',
         "index": 0}
    )
    create_category_token = 'categorylidarsegcategory00000001'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Buildings',
         'description': 'Buildings',
         "index": 1}
    )
    create_category_token = 'categorylidarsegcategory00000002'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Fences',
         'description': 'Fences',
         "index": 2}
    )
    create_category_token = 'categorylidarsegcategory00000003'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Other',
         'description': 'Other',
         "index": 3}
    )
    create_category_token = 'categorylidarsegcategory00000004'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Pedestrians',
         'description': 'Pedestrians',
         "index": 4}
    )
    create_category_token = 'categorylidarsegcategory00000005'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Poles',
         'description': 'Poles',
         "index": 5}
    )
    create_category_token = 'categorylidarsegcategory00000006'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'RoadLines',
         'description': 'RoadLines',
         "index": 6}
    )
    create_category_token = 'categorylidarsegcategory00000007'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Roads',
         'description': 'Roads',
         "index": 7}
    )
    create_category_token = 'categorylidarsegcategory00000008'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Sidewalks',
         'description': 'Sidewalks',
         "index": 8}
    )
    create_category_token = 'categorylidarsegcategory00000009'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Vegetation',
         'description': 'Vegetation',
         "index": 9}
    )
    create_category_token = 'categorylidarsegcategory00000010'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Vehicles',
         'description': 'Vehicles',
         "index": 10}
    )
    create_category_token = 'categorylidarsegcategory00000011'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Walls',
         'description': 'Walls',
         "index": 11}
    )
    create_category_token = 'categorylidarsegcategory00000012'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'TrafficSigns',
         'description': 'TrafficSigns',
         "index": 12}
    )
    create_category_token = 'categorylidarsegcategory00000013'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Sky',
         'description': 'Sky',
         "index": 13}
    )
    create_category_token = 'categorylidarsegcategory00000014'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Ground',
         'description': 'Ground',
         "index": 14}
    )
    create_category_token = 'categorylidarsegcategory00000015'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Bridge',
         'description': 'Bridge',
         "index": 15}
    )
    create_category_token = 'categorylidarsegcategory00000016'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'RailTrack',
         'description': 'RailTrack',
         "index": 16}
    )
    create_category_token = 'categorylidarsegcategory00000017'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'GuardRail',
         'description': 'GuardRail',
         "index": 17}
    )
    create_category_token = 'categorylidarsegcategory00000018'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'TrafficLight',
         'description': 'TrafficLight',
         "index": 18}
    )
    create_category_token = 'categorylidarsegcategory00000019'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Static',
         'description': 'Static',
         "index": 19}
    )
    create_category_token = 'categorylidarsegcategory00000020'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Dynamic',
         'description': 'Dynamic',
         "index": 20}
    )
    create_category_token = 'categorylidarsegcategory00000021'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Water',
         'description': 'Water',
         "index": 21}
    )
    create_category_token = 'categorylidarsegcategory00000022'
    lidarseg_category_json.append(
        {'token': create_category_token,
         'name': 'Terrain',
         'description': 'Terrain',
         "index": 22}
    )
    lidarseg_category_jsondata = json.dumps(lidarseg_category_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/lidarseg_category.json', 'w')
    f.write(lidarseg_category_jsondata)
    f.close()


def create_attribute_json(attribute_json):
    create_attribute_token = 'vehiclemovingvehiclemovingvehicl'
    attribute_json.append(
        {'token': create_attribute_token,
         'name': 'vehicle.moving',
         'description': 'Vehicle is moving.'}
    )

    create_attribute_token = 'cyclewithridercyclewithridercycl'
    attribute_json.append(
        {'token': create_attribute_token,
         'name': 'cycle.with_rider',
         'description': 'There is a rider on the bicycle or motorcycle.'}
    )

    create_attribute_token = 'pedestrianmovingpedestrianmoving'
    attribute_json.append(
        {'token': create_attribute_token,
         'name': 'pedestrian.moving',
         'description': 'The human is moving.'}
    )

    attribute_jsondata = json.dumps(attribute_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/attribute.json', 'w')
    f.write(attribute_jsondata)
    f.close()


def create_log_json(log_json):
    log_json.append(
        {'token': 'logtokenlogtokenlogtokenlogtoken',
         'logfile': 'n008-2018-08-01-00-00-00-0400',
         'vehicle': 'n008',
         'date_captured': '2018-08-01',
         'location': 'singapore-onenorth'}
    )
    log_jsondata = json.dumps(log_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/log.json', 'w')
    f.write(log_jsondata)
    f.close()


def create_map_json(map_json):
    map_json.append({
        "category": "semantic_prior",
        "token": "53992ee3023e5494b90c316c183be829",
        "filename": "maps/53992ee3023e5494b90c316c183be829.png",
        "log_tokens": [
        "logtokenlogtokenlogtokenlogtoken"
        ]
    })
    map_jsondata = json.dumps(map_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/map.json', 'w')
    f.write(map_jsondata)
    f.close()


def create_calibrated_sensor_json(calibrated_sensor_json, sensor_list):
    create_sensor_token = None
    create_calibrated_sensor_token = None
    for s in sensor_list:
        if s == 'LIDAR_TOP':
            create_sensor_token = 'lidartoplidartoplidartoplidartop'
            create_calibrated_sensor_token = '90000000000000000000000000000000'
            translation = [0, 0, 1.8]
            rotation = [
                0.707, 0, 0, -0.707
            ]
            camera_intrinsic = []
        if s == 'CAM_FRONT':
            create_sensor_token = 'camfrontcamfrontcamfrontcamfront'
            create_calibrated_sensor_token = '90000000000000000000000000000001'
            translation = [0.5, 0, 1.8]
            rotation = [
                0.5, -0.5, 0.5, -0.5
            ]
            camera_intrinsic = [
                [1142.53, 0.0, 800],
                [0.0, 1142.53, 450],
                [0.0, 0.0, 1.0]
            ]
        if s == 'CAM_BACK':
            create_sensor_token = 'cambackcambackcambackcambackcamb'
            create_calibrated_sensor_token = '90000000000000000000000000000002'
            translation = [-1.5, 0, 1.8]
            rotation = [
                0.5, -0.5, -0.5, 0.5
            ]
            camera_intrinsic = [
                [560.166, 0.0, 800],
                [0.0, 560.166, 450],
                [0.0, 0.0, 1.0]
            ]
        if s == 'CAM_FRONT_LEFT':
            create_sensor_token = 'camfrontleftcamfrontleftcamfront'
            create_calibrated_sensor_token = '90000000000000000000000000000003'
            translation = [0, 0.5, 1.8]
            rotation = [
                0.674,
                -0.674,
                0.213,
                -0.213
            ]
            camera_intrinsic = [
                [1142.53, 0.0, 800],
                [0.0, 1142.53, 450],
                [0.0, 0.0, 1.0]
            ]
        if s == 'CAM_FRONT_RIGHT':
            create_sensor_token = 'camfrontrightcamfrontrightcamfro'
            create_calibrated_sensor_token = '90000000000000000000000000000004'
            translation = [0, -0.5, 1.8]
            rotation = [
                0.213,
                -0.213,
                0.674,
                -0.674
            ]
            camera_intrinsic = [
                [1142.53, 0.0, 800],
                [0.0, 1142.53, 450],
                [0.0, 0.0, 1.0]
            ]
        if s == 'CAM_BACK_LEFT':
            create_sensor_token = 'cambackleftcambackleftcambacklef'
            create_calibrated_sensor_token = '90000000000000000000000000000005'
            translation = [-0.5, 0.5, 1.8]
            rotation = [
                0.696,
                -0.696,
                -0.123,
                0.123
            ]
            camera_intrinsic = [
                [1142.53, 0.0, 800],
                [0.0, 1142.53, 450],
                [0.0, 0.0, 1.0]
            ]
        if s == 'CAM_BACK_RIGHT':
            create_sensor_token = 'cambackrightcambackrightcambackr'
            create_calibrated_sensor_token = '90000000000000000000000000000006'
            translation = [-0.5, -0.5, 1.8]
            rotation = [
                0.123,
                -0.123,
                -0.696,
                0.696
            ]
            camera_intrinsic = [
                [1142.53, 0.0, 800],
                [0.0, 1142.53, 450],
                [0.0, 0.0, 1.0]
            ]

        calibrated_sensor_json.append(
            {'token': create_calibrated_sensor_token,
             'sensor_token': create_sensor_token,
             'translation': translation,
             'rotation': rotation,
             'camera_intrinsic': camera_intrinsic}
        )
    calibrated_sensor_jsondata = json.dumps(calibrated_sensor_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/calibrated_sensor.json', 'w')
    f.write(calibrated_sensor_jsondata)
    f.close()


# write json file
def nuread(pathh):
    files = os.listdir(pathh)
    scene_json = []
    sensor_json = []
    calibrated_sensor_json = []
    log_json = []
    sample_json = []
    sample_annotation_json = []
    sample_data_json = []
    instance_json = []
    ego_pose_json = []
    attribute_json = []

    lidarseg_category_json = []
    visibility_json = []
    map_json = []
    lidarseg_json = []

    sensor_list = ['LIDAR_TOP', 'CAM_BACK', 'CAM_BACK_LEFT', 'CAM_BACK_RIGHT',
                   'CAM_FRONT', 'CAM_FRONT_LEFT', 'CAM_FRONT_RIGHT']

    # timestamp
    timestamp = 0

    # calibrated_sensor_token
    calibrated_sensor_token = 0

    # scene_name
    scene_name = 1001

    # scene_token
    scene_token = 70000000000000000000000000000001

    # sample_token
    sample_token = 10000000000000000000000000000001

    # sample_annotation_token
    sample_annotation_token = 20000000000000000000000000000001

    # ego_pose_token
    ego_pose_token = 0

    # sample_data_token
    sample_data_token_lidar_top = 30000000000000000000000000000001

    sample_data_token_cam_front = 30100000000000000000000000000001

    sample_data_token_cam_back = 30200000000000000000000000000001

    sample_data_token_cam_front_left = 30300000000000000000000000000001

    sample_data_token_cam_front_right = 30400000000000000000000000000001

    sample_data_token_cam_back_left = 30500000000000000000000000000001

    sample_data_token_cam_back_right = 30600000000000000000000000000001


    # instance_token
    instance_token = 40000000000000000000000000000001

    category_token = None

    attribute_tokens = None

    # open txt file
    for i in range(1, 40000):
        file_no = 1500000000000000 + i

        f = str(file_no)
        if f[-3] != 'x':

            # timestamp
            print('--- New task ---')
            print('Past:', timestamp)
            # timestamp = file.split('.')[0]
            timestamp = str(file_no)
            print('Next:', timestamp)

            # open position
            # position = pathh + '/' + file
            position = pathh + '/' + str(file_no) + '.txt'

            if os.path.exists(position):
                datas = openreadtxt(position)
            else:
                continue
            print('Generating...')

            if sample_token % 40 == 1:
                sample_json.append(
                    {'token': str(sample_token),
                     'timestamp': int(timestamp),
                     'prev': '',
                     'next': str(sample_token + 1),
                     'scene_token': str(scene_token)}
                )
            elif sample_token % 40 == 0:
                sample_json.append(
                    {'token': str(sample_token),
                     'timestamp': int(timestamp),
                     'prev': str(sample_token - 1),
                     'next': '',
                     'scene_token': str(scene_token)}
                )
            else:
                sample_json.append(
                    {'token': str(sample_token),
                     'timestamp': int(timestamp),
                     'prev': str(sample_token - 1),
                     'next': str(sample_token + 1),
                     'scene_token': str(scene_token)}
                )

            for s in sensor_list:
                if s == 'LIDAR_TOP':
                    fileformat = 'pcd'
                    forma = '.pcd.bin'
                    height = 0
                    width = 0
                    calibrated_sensor_token = '90000000000000000000000000000000'
                    ego_pose_token = sample_data_token_lidar_top

                    lidarseg_json.append(
                        {'token': str(sample_data_token_lidar_top),
                         'sample_data_token': str(sample_data_token_lidar_top),
                         'filename': "lidarseg/v1.0-trainval/" + str(sample_data_token_lidar_top) + "_lidarseg.bin"}
                    )

                else:
                    fileformat = 'jpg'
                    forma = '.jpg'
                    height = 900
                    width = 1600
                    if s == 'CAM_FRONT':
                        calibrated_sensor_token = '90000000000000000000000000000001'
                        ego_pose_token = sample_data_token_cam_front
                    if s == 'CAM_BACK':
                        calibrated_sensor_token = '90000000000000000000000000000002'
                        ego_pose_token = sample_data_token_cam_back
                    if s == 'CAM_FRONT_LEFT':
                        calibrated_sensor_token = '90000000000000000000000000000003'
                        ego_pose_token = sample_data_token_cam_front_left
                    if s == 'CAM_FRONT_RIGHT':
                        calibrated_sensor_token = '90000000000000000000000000000004'
                        ego_pose_token = sample_data_token_cam_front_right
                    if s == 'CAM_BACK_LEFT':
                        calibrated_sensor_token = '90000000000000000000000000000005'
                        ego_pose_token = sample_data_token_cam_back_left
                    if s == 'CAM_BACK_RIGHT':
                        calibrated_sensor_token = '90000000000000000000000000000006'
                        ego_pose_token = sample_data_token_cam_back_right

                filename = 'samples/' + s + '/n008-2018-08-01-00-00-00-0400__' + s + '__' + timestamp + forma

                if sample_token % 40 == 1:
                    sample_data_json.append(
                        {'token': str(ego_pose_token),
                         'sample_token': str(sample_token),
                         'ego_pose_token': str(ego_pose_token),
                         'calibrated_sensor_token': calibrated_sensor_token,
                         'timestamp': int(timestamp),
                         'fileformat': fileformat,
                         'is_key_frame': True,
                         'height': height,
                         'width': width,
                         'filename': filename,
                         'prev': '',
                         'next': str(ego_pose_token + 1)}
                    )
                elif sample_token % 40 == 0:
                    sample_data_json.append(
                        {'token': str(ego_pose_token),
                         'sample_token': str(sample_token),
                         'ego_pose_token': str(ego_pose_token),
                         'calibrated_sensor_token': calibrated_sensor_token,
                         'timestamp': int(timestamp),
                         'fileformat': fileformat,
                         'is_key_frame': True,
                         'height': height,
                         'width': width,
                         'filename': filename,
                         'prev': str(ego_pose_token - 1),
                         'next': ''}
                    )
                else:
                    sample_data_json.append(
                        {'token': str(ego_pose_token),
                         'sample_token': str(sample_token),
                         'ego_pose_token': str(ego_pose_token),
                         'calibrated_sensor_token': calibrated_sensor_token,
                         'timestamp': int(timestamp),
                         'fileformat': fileformat,
                         'is_key_frame': True,
                         'height': height,
                         'width': width,
                         'filename': filename,
                         'prev': str(ego_pose_token - 1),
                         'next': str(ego_pose_token + 1)}
                    )

                ego_pose_json.append(
                    {'token': str(ego_pose_token),
                     'timestamp': int(timestamp),
                     'rotation': [1, 0, 0, 0],
                     'translation': [0, 0, 0]}
                )

            # next sample_data_token
            sample_data_token_lidar_top = sample_data_token_lidar_top + 1
            sample_data_token_cam_front = sample_data_token_cam_front + 1
            sample_data_token_cam_back = sample_data_token_cam_back + 1
            sample_data_token_cam_front_left = sample_data_token_cam_front_left + 1
            sample_data_token_cam_front_right = sample_data_token_cam_front_right + 1
            sample_data_token_cam_back_left = sample_data_token_cam_back_left + 1
            sample_data_token_cam_back_right = sample_data_token_cam_back_right + 1

            c_i = 0
            H, W, L, X, Y, Z, D, theta, pool, result = [], [], [], [], [], [], [], [], [], []

            for data in datas:
                H.append(float(data[8]))
                W.append(float(data[9]))
                L.append(float(data[10]))
                X.append(float(data[11]))
                Y.append(float(data[12]))
                Z.append(float(data[13]))
                # D.append(sqrt(X[c_i] ** 2 + Z[c_i] ** 2))
                theta.append(float(data[14]))

                z1, z2 = [], []

                R = [[cos(theta[c_i]), sin(theta[c_i])], [-sin(theta[c_i]), cos(theta[c_i])]]
                T = [X[c_i], Z[c_i]]


                pp = [L[c_i] / 2, W[c_i] / 2]
                x1, y1 = np.matmul(R, pp) + T
                z1.append(Y[c_i] / sqrt(x1 ** 2 + y1 ** 2))
                z2.append((Y[c_i] - H[c_i]) / sqrt(x1 ** 2 + y1 ** 2))
                if x1 >= 0 and y1 >= 0:
                    psi0 = atan(x1 / y1)
                if x1 < 0 and y1 >= 0:
                    psi0 = atan(x1 / y1)
                if x1 < 0 and y1 < 0:
                    psi0 = atan(x1 / y1) - pi
                if x1 >= 0 and y1 < 0:
                    psi0 = atan(x1 / y1) + pi


                pp = [-L[c_i] / 2, W[c_i] / 2]
                x1, y1 = np.matmul(R, pp) + T
                z1.append(Y[c_i] / sqrt(x1 ** 2 + y1 ** 2))
                z2.append((Y[c_i] - H[c_i]) / sqrt(x1 ** 2 + y1 ** 2))
                if x1 >= 0 and y1 >= 0:
                    psi1 = atan(x1 / y1)
                if x1 < 0 and y1 >= 0:
                    psi1 = atan(x1 / y1)
                if x1 < 0 and y1 < 0:
                    psi1 = atan(x1 / y1) - pi
                if x1 >= 0 and y1 < 0:
                    psi1 = atan(x1 / y1) + pi


                pp = [-L[c_i] / 2, -W[c_i] / 2]
                x1, y1 = np.matmul(R, pp) + T
                z1.append(Y[c_i] / sqrt(x1 ** 2 + y1 ** 2))
                z2.append((Y[c_i] - H[c_i]) / sqrt(x1 ** 2 + y1 ** 2))
                if x1 >= 0 and y1 >= 0:
                    psi2 = atan(x1 / y1)
                if x1 < 0 and y1 >= 0:
                    psi2 = atan(x1 / y1)
                if x1 < 0 and y1 < 0:
                    psi2 = atan(x1 / y1) - pi
                if x1 >= 0 and y1 < 0:
                    psi2 = atan(x1 / y1) + pi


                pp = [L[c_i] / 2, -W[c_i] / 2]
                x1, y1 = np.matmul(R, pp) + T
                z1.append(Y[c_i] / sqrt(x1 ** 2 + y1 ** 2))
                z2.append((Y[c_i] - H[c_i]) / sqrt(x1 ** 2 + y1 ** 2))
                if x1 >= 0 and y1 >= 0:
                    psi3 = atan(x1 / y1)
                if x1 < 0 and y1 >= 0:
                    psi3 = atan(x1 / y1)
                if x1 < 0 and y1 < 0:
                    psi3 = atan(x1 / y1) - pi
                if x1 >= 0 and y1 < 0:
                    psi3 = atan(x1 / y1) + pi

                if max(psi0, psi1, psi2, psi3) - min(psi0, psi1, psi2, psi3) > pi:
                    if psi0 < 0:
                        psi0 += 2 * pi
                    if psi1 < 0:
                        psi1 += 2 * pi
                    if psi2 < 0:
                        psi2 += 2 * pi
                    if psi3 < 0:
                        psi3 += 2 * pi
                    pool.append(
                        [[psi0, z1[0]], [psi0, z2[0]], [psi1, z1[1]], [psi1, z2[1]], [psi2, z1[2]], [psi2, z2[2]],
                         [psi3, z1[3]], [psi3, z2[3]]])
                    D.append(sqrt(X[c_i] ** 2 + Z[c_i] ** 2))

                elif min(psi0, psi1, psi2, psi3) < 0:
                    pool.append(
                        [[psi0, z1[0]], [psi0, z2[0]], [psi1, z1[1]], [psi1, z2[1]], [psi2, z1[2]], [psi2, z2[2]],
                         [psi3, z1[3]], [psi3, z2[3]]])
                    D.append(sqrt(X[c_i] ** 2 + Z[c_i] ** 2))
                    psi0 += 2 * pi
                    psi1 += 2 * pi
                    psi2 += 2 * pi
                    psi3 += 2 * pi
                    pool.append(
                        [[psi0, z1[0]], [psi0, z2[0]], [psi1, z1[1]], [psi1, z2[1]], [psi2, z1[2]], [psi2, z2[2]],
                         [psi3, z1[3]], [psi3, z2[3]]])
                    D.append(sqrt(X[c_i] ** 2 + Z[c_i] ** 2))

                else:
                    pool.append(
                        [[psi0, z1[0]], [psi0, z2[0]], [psi1, z1[1]], [psi1, z2[1]], [psi2, z1[2]], [psi2, z2[2]],
                         [psi3, z1[3]], [psi3, z2[3]]])
                    D.append(sqrt(X[c_i] ** 2 + Z[c_i] ** 2))


                c_i += 1

            for data in datas:
                if data[0] == 'car':
                    category_token = 'categorylidarsegcategory00000010'
                    attribute_tokens = 'vehiclemovingvehiclemovingvehicl'
                    # print(data)
                elif data[0] == 'truck' or data[0] == 'bus':
                    category_token = 'categorylidarsegcategory00000010'
                    attribute_tokens = 'vehiclemovingvehiclemovingvehicl'
                    # print(data)

                elif data[0] == 'bicycle' or data[0] == 'motorcycle':
                    category_token = 'categorylidarsegcategory00000010'
                    attribute_tokens = 'cyclewithridercyclewithridercycl'
                    # print(data)

                elif data[0] == 'pedestrian':
                    category_token = 'categorylidarsegcategory00000004'
                    attribute_tokens = 'pedestrianmovingpedestrianmoving'
                    # print(data)

                else:
                    with open('error.txt', 'w') as ftt:
                        ftt.write('Error!')

                x0 = float(data[11])
                y0 = float(data[12])
                z0 = float(data[13])
                h0 = float(data[8])
                w0 = float(data[9])
                l0 = float(data[10])
                d0 = sqrt(x0 ** 2 + z0 ** 2)
                theta0 = float(data[14])
                s = []
                p_pool = []
                for D_i in range(len(D)):
                    if d0 > D[D_i]:
                        s.append(D_i)

                for s_i in range(len(s)):
                    p_pool.append(pool[s[s_i]])
                    # print(p_pool)

                z1, z2 = [], []

                R = [[cos(theta0), sin(theta0)], [-sin(theta0), cos(theta0)]]
                T = [x0, z0]

                pp = [l0 / 2, w0 / 2]
                x1, y1 = np.matmul(R, pp) + T
                z1.append(y0 / sqrt(x1 ** 2 + y1 ** 2))
                z2.append((y0 - h0) / sqrt(x1 ** 2 + y1 ** 2))
                if x1 >= 0 and y1 >= 0:
                    psi0 = atan(x1 / y1)
                if x1 < 0 and y1 >= 0:
                    psi0 = atan(x1 / y1)
                if x1 < 0 and y1 < 0:
                    psi0 = atan(x1 / y1) - pi
                if x1 >= 0 and y1 < 0:
                    psi0 = atan(x1 / y1) + pi

                pp = [-l0 / 2, w0 / 2]
                x1, y1 = np.matmul(R, pp) + T
                z1.append(y0 / sqrt(x1 ** 2 + y1 ** 2))
                z2.append((y0 - h0) / sqrt(x1 ** 2 + y1 ** 2))
                if x1 >= 0 and y1 >= 0:
                    psi1 = atan(x1 / y1)
                if x1 < 0 and y1 >= 0:
                    psi1 = atan(x1 / y1)
                if x1 < 0 and y1 < 0:
                    psi1 = atan(x1 / y1) - pi
                if x1 >= 0 and y1 < 0:
                    psi1 = atan(x1 / y1) + pi

                pp = [-l0 / 2, -w0 / 2]
                x1, y1 = np.matmul(R, pp) + T
                z1.append(y0 / sqrt(x1 ** 2 + y1 ** 2))
                z2.append((y0 - h0) / sqrt(x1 ** 2 + y1 ** 2))
                if x1 >= 0 and y1 >= 0:
                    psi2 = atan(x1 / y1)
                if x1 < 0 and y1 >= 0:
                    psi2 = atan(x1 / y1)
                if x1 < 0 and y1 < 0:
                    psi2 = atan(x1 / y1) - pi
                if x1 >= 0 and y1 < 0:
                    psi2 = atan(x1 / y1) + pi

                pp = [l0 / 2, -w0 / 2]
                x1, y1 = np.matmul(R, pp) + T
                z1.append(y0 / sqrt(x1 ** 2 + y1 ** 2))
                z2.append((y0 - h0) / sqrt(x1 ** 2 + y1 ** 2))
                if x1 >= 0 and y1 >= 0:
                    psi3 = atan(x1 / y1)
                if x1 < 0 and y1 >= 0:
                    psi3 = atan(x1 / y1)
                if x1 < 0 and y1 < 0:
                    psi3 = atan(x1 / y1) - pi
                if x1 >= 0 and y1 < 0:
                    psi3 = atan(x1 / y1) + pi

                if max(psi0, psi1, psi2, psi3) - min(psi0, psi1, psi2, psi3) > pi:
                    if psi0 < 0:
                        psi0 += 2 * pi
                    if psi1 < 0:
                        psi1 += 2 * pi
                    if psi2 < 0:
                        psi2 += 2 * pi
                    if psi3 < 0:
                        psi3 += 2 * pi
                    p_point = [[psi0, z1[0]], [psi0, z2[0]], [psi1, z1[1]], [psi1, z2[1]], [psi2, z1[2]], [psi2, z2[2]],
                         [psi3, z1[3]], [psi3, z2[3]]]

                elif max(psi0, psi1, psi2, psi3) < 0:
                    psi0 += 2 * pi
                    psi1 += 2 * pi
                    psi2 += 2 * pi
                    psi3 += 2 * pi
                    p_point = [[psi0, z1[0]], [psi0, z2[0]], [psi1, z1[1]], [psi1, z2[1]], [psi2, z1[2]], [psi2, z2[2]],
                               [psi3, z1[3]], [psi3, z2[3]]]

                else:
                    p_point = [[psi0, z1[0]], [psi0, z2[0]], [psi1, z1[1]], [psi1, z2[1]], [psi2, z1[2]], [psi2, z2[2]],
                               [psi3, z1[3]], [psi3, z2[3]]]

                points_sets = np.array(p_pool)

                polygons = [points_to_convex_polygon(points) for points in points_sets]

                target_polygon = points_to_convex_polygon(np.array(p_point))

                original_area = target_polygon.area

                overlapping_polygons = [p for p in polygons if p != target_polygon and p.intersects(target_polygon)]

                overlapping_area = sum(target_polygon.intersection(p).area for p in overlapping_polygons)

                non_overlapping_area = original_area - overlapping_area

                non_overlapping_ratio = non_overlapping_area / original_area

                # print(f"original_area: {original_area}")
                # print(f"overlapping_area: {overlapping_area}")
                # print(f"non_overlapping_ratio: {non_overlapping_ratio}")

                if non_overlapping_ratio >= 0.9:
                    visibility_token = 4
                elif non_overlapping_ratio >= 0.6:
                    visibility_token = 3
                elif non_overlapping_ratio >= 0.3:
                    visibility_token = 2
                else:
                    visibility_token = 1

                rotation1 = [cos((- float(data[14]) - pi / 2) / 2), 0, 0, sin((- float(data[14]) - pi / 2) / 2)]

                sample_annotation_json.append({
                    'token': str(sample_annotation_token),
                    'sample_token': str(sample_token),
                    'instance_token': str(instance_token),
                    'visibility_token': str(visibility_token),
                    'attribute_tokens': [
                        attribute_tokens
                        ],
                    'translation': [float(data[13]), - float(data[11]), 1.8 - float(data[12]) + float(data[8]) / 2],  #
                    'size': [float(data[9]), float(data[10]), float(data[8])],
                    'rotation': rotation1,
                    'prev': '',
                    'next': '',
                    'num_lidar_pts': 10,
                    'num_radar_pts': 0
                })

                # else:
                #     sample_annotation_json.append({
                #         'token': str(sample_annotation_token),
                #         'sample_token': str(sample_token),
                #         'instance_token': str(instance_token),
                #         'visibility_token': '4',
                #         'attribute_tokens': attribute_tokens,
                #         'translation': [float(data[13]), - float(data[11]), float(data[8]) / 2],  #
                #         'size': [float(data[9]), float(data[10]), float(data[8])],
                #         'rotation': rotation1,
                #         'prev': str(sample_annotation_token - 1),
                #         'next': str(sample_annotation_token + 1),
                #         'num_lidar_pts': 10,
                #         'num_radar_pts': 0
                #     })

                instance_json.append(
                    {'token': str(instance_token),
                     'category_token': category_token,
                     'nbr_annotations': 1,
                     'first_annotation_token': str(sample_annotation_token),
                     'last_annotation_token': str(sample_annotation_token)}
                )

                sample_annotation_token = sample_annotation_token + 1
                instance_token = instance_token + 1

            if sample_token % 40 == 0:
                name = 'carla-' + str(scene_name)
                scene_json.append(
                    {'token': str(scene_token),
                     'log_token': 'logtokenlogtokenlogtokenlogtoken',
                     'nbr_samples': 40,
                     'first_sample_token': str(sample_token - 39),
                     'last_sample_token': str(sample_token),
                     'name': name,
                     'description': 'carla'}
                )
                scene_token = scene_token + 1
                scene_name = scene_name + 1

            # next sample
            sample_token = sample_token + 1

        # scene_json.append(
        #     {'token': 'scenetoken0scenetoken0scenetoken',
        #      'log_token': 'logtokenlogtokenlogtokenlogtoken',
        #      'nbr_samples': sample_token - 10000000000000000000000000000000,
        #      'first_sample_token': str(10000000000000000000000000000001),
        #      'last_sample_token': str(sample_token),
        #      'name': 'carla-0001',
        #      'description': 'carla'}
        # )

    name = 'carla-' + str(scene_name)
    scene_json.append(
        {'token': str(scene_token),
         'log_token': 'logtokenlogtokenlogtokenlogtoken',
         'nbr_samples': (sample_token - 1) % 40,
         'first_sample_token': str(sample_token - 1 - ((sample_token - 1) % 40) + 1),
         'last_sample_token': str(sample_token - 1),
         'name': name,
         'description': 'carla'}
    )

    scene_jsondata = json.dumps(scene_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/scene.json', 'w')
    f.write(scene_jsondata)
    f.close()

    sample_jsondata = json.dumps(sample_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/sample.json', 'w')
    f.write(sample_jsondata)
    f.close()

    sample_annotation_jsondata = json.dumps(sample_annotation_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/sample_annotation.json', 'w')
    f.write(sample_annotation_jsondata)
    f.close()

    instance_jsondata = json.dumps(instance_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/instance.json', 'w')
    f.write(instance_jsondata)
    f.close()

    sample_data_jsondata = json.dumps(sample_data_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/sample_data.json', 'w')
    f.write(sample_data_jsondata)
    f.close()

    ego_pose_jsondata = json.dumps(ego_pose_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/ego_pose.json', 'w')
    f.write(ego_pose_jsondata)
    f.close()

    lidarseg_jsondata = json.dumps(lidarseg_json, indent=4, separators=(',', ':'))
    f = open('v1.0-trainval/lidarseg.json', 'w')
    f.write(lidarseg_jsondata)
    f.close()

    create_sensor_json(sensor_json, sensor_list)
    create_calibrated_sensor_json(calibrated_sensor_json, sensor_list)

    create_lidarseg_category_json(lidarseg_category_json)
    create_visibility_json(visibility_json)
    create_attribute_json(attribute_json)
    create_log_json(log_json)
    create_map_json(map_json)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    os.makedirs("v1.0-trainval", exist_ok=True)
    pat = "./label_2"
    nuread(pat)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
