import sys
import math

sys.path.append(
    "./carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg"
)

import toml
import carla

from constants import CAMERA_IMAGE_X, CAMERA_IMAGE_Y
# from constants import *


class LiDARSetup(object):
    def __init__(self, param_file, world, ego, callback_handler, setup=False):
        params = toml.load(f"../hyperparams/{param_file}")['lidar']
        self.world = world
        self.ego = ego
        self.callback_handler = callback_handler
        self.num = params["num"]
        self.sets = params["sets"]
        self.channels = params["channels"]
        self.lower_fov = params["lower_fov"]
        self.upper_fov = params["upper_fov"]
        self.x = params["x"]
        self.y = params["y"]
        self.z = params["z"]
        self.roll = params["roll"]
        self.pitch = params["pitch"]
        self.lidar_range_in_meters = params["lidar_range_in_meters"]
        self.rotation_frequency = params["rotation_frequency"]
        self.points_per_channel = params["points_per_channel"]
        self.stats = {}
        if setup:
            # self._check_for_errors()
            self._setup()
        else:
            pass

    def _check_for_errors(self):
        return True

    def _setup(self):
        self.stats["h"] = {}
        self.stats["t"] = {}
        self.stats["l"] = {}

    def process_render_object(self, instance, data):
        data["points"][instance[1]] = instance[0]
        return data

    def destroy(self):
        for i in range(self.num):
            self.stats['l'][i].destroy()

    def create_lidar_spec(self):
        """
        Define the sensors spec as required by the Scenario Runner

        :return: a list containing the required sensors in the following format:

        [
            {'type': 'sensor.camera.rgb', 'x': 0.7, 'y': -0.4, 'z': 1.60, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0,
                      'width': 300, 'height': 200, 'fov': 100, 'id': 'Left'},

            {'type': 'sensor.camera.rgb', 'x': 0.7, 'y': 0.4, 'z': 1.60, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0,
                      'width': 300, 'height': 200, 'fov': 100, 'id': 'Right'},

            {'type': 'sensor.lidar.ray_cast', 'x': 0.7, 'y': 0.0, 'z': 1.60, 'yaw': 0.0, 'pitch': 0.0, 'roll': 0.0,
             'id': 'LIDAR'}
        ]

        """
        specs = []

        for i in range(self.sets):
            for j in range(self.num[i]):
                spec = {}
                spec['x'], spec['y'], spec['z'] = self.x[i][j], self.y[i][j], self.z[i][j]
                spec['roll'], spec['pitch'], spec['yaw'] = self.roll[i][j], self.pitch[i][j], 0
                spec["noise_stddev"] = "0.2"

                spec["upper_fov"] = str(self.upper_fov[i][j])
                spec["lower_fov"] = str(self.lower_fov[i][j])
                spec["channels"] = str(self.channels[i][j])

                spec["range"] = str(self.lidar_range_in_meters[i][j])
                spec["rotation_frequency"] = str(self.rotation_frequency[i][j])
                spec["points_per_second"] = str(self.points_per_channel[i][j] * self.channels[i][j]) 
                
                spec["id"] = f"l_{i}{j}"
                spec["type"] = "sensor.lidar.ray_cast_semantic"

                specs.append(spec)

        return specs


class Sensor(object):
    def __init__(self, param_file, lidars):
        self.lidars = lidars
        self.cams = toml.load(f"../hyperparams/{param_file}")['camera']
        self.lids = toml.load(f"../hyperparams/{param_file}")['lidar']

    def create_sensor_spec(self):
        """
        Define the sensors spec as required by the Scenario Runner

        :return: a list containing the required sensors in the following format:

        [
            {'type': 'sensor.camera.rgb', 'x': 0.7, 'y': -0.4, 'z': 1.60, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0,
                      'width': 300, 'height': 200, 'fov': 100, 'id': 'Left'},

            {'type': 'sensor.camera.rgb', 'x': 0.7, 'y': 0.4, 'z': 1.60, 'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0,
                      'width': 300, 'height': 200, 'fov': 100, 'id': 'Right'},

            {'type': 'sensor.lidar.ray_cast', 'x': 0.7, 'y': 0.0, 'z': 1.60, 'yaw': 0.0, 'pitch': 0.0, 'roll': 0.0,
             'id': 'LIDAR'}
        ]

        """

        specs = self.lidars.create_lidar_spec()
        camera_spec = {}
        camera_spec['width'] = str(CAMERA_IMAGE_X)
        camera_spec['height'] = str(CAMERA_IMAGE_Y)
        camera_spec["fov"] = str(90.0)
        camera_spec['id'] = "camera01"
        camera_spec['x'], camera_spec['y'], camera_spec['z'] = 0.0, 0.0, self.lids['GLOBAL_HEIGHT_POS']
        camera_spec['roll'], camera_spec['pitch'], camera_spec['yaw'] = 0.0, 0.0, 0.0
        camera_spec['type'] = 'sensor.camera.rgb'
        camera_spec['motion_blur_intensity'] = 0

        cam_front_spec = {}
        cam_front_spec['width'] = str(CAMERA_IMAGE_X)
        cam_front_spec['height'] = str(CAMERA_IMAGE_Y)
        cam_front_spec["fov"] = str(self.cams['FOV_CAM_FRONT'])
        cam_front_spec['id'] = "cam_front01"
        cam_front_spec['x'], cam_front_spec['y'], cam_front_spec['z'] = self.cams['T_CAM_FRONT']
        cam_front_spec['roll'], cam_front_spec['pitch'], cam_front_spec['yaw'] = self.cams['R_CAM_FRONT']
        cam_front_spec['type'] = 'sensor.camera.rgb'
        cam_front_spec['motion_blur_intensity'] = 0

        cam_front_left_spec = {}
        cam_front_left_spec['width'] = str(CAMERA_IMAGE_X)
        cam_front_left_spec['height'] = str(CAMERA_IMAGE_Y)
        cam_front_left_spec["fov"] = str(self.cams['FOV_CAM_FRONT_LEFT'])
        cam_front_left_spec['id'] = "cam_front_left01"
        cam_front_left_spec['x'], cam_front_left_spec['y'], cam_front_left_spec['z'] = self.cams['T_CAM_FRONT_LEFT']
        cam_front_left_spec['roll'], cam_front_left_spec['pitch'], cam_front_left_spec['yaw'] = self.cams['R_CAM_FRONT_LEFT']
        cam_front_left_spec['type'] = 'sensor.camera.rgb'
        cam_front_left_spec['motion_blur_intensity'] = 0

        cam_front_right_spec = {}
        cam_front_right_spec['width'] = str(CAMERA_IMAGE_X)
        cam_front_right_spec['height'] = str(CAMERA_IMAGE_Y)
        cam_front_right_spec["fov"] = str(self.cams['FOV_CAM_FRONT_RIGHT'])
        cam_front_right_spec['id'] = "cam_front_right01"
        cam_front_right_spec['x'], cam_front_right_spec['y'], cam_front_right_spec['z'] = self.cams['T_CAM_FRONT_RIGHT']
        cam_front_right_spec['roll'], cam_front_right_spec['pitch'], cam_front_right_spec['yaw'] = self.cams['R_CAM_FRONT_RIGHT']
        cam_front_right_spec['type'] = 'sensor.camera.rgb'
        cam_front_right_spec['motion_blur_intensity'] = 0

        cam_back_spec = {}
        cam_back_spec['width'] = str(CAMERA_IMAGE_X)
        cam_back_spec['height'] = str(CAMERA_IMAGE_Y)
        cam_back_spec["fov"] = str(self.cams['FOV_CAM_BACK'])
        cam_back_spec['id'] = "cam_back01"
        cam_back_spec['x'], cam_back_spec['y'], cam_back_spec['z'] = self.cams['T_CAM_BACK']
        cam_back_spec['roll'], cam_back_spec['pitch'], cam_back_spec['yaw'] = self.cams['R_CAM_BACK']
        cam_back_spec['type'] = 'sensor.camera.rgb'
        cam_back_spec['motion_blur_intensity'] = 0

        cam_back_left_spec = {}
        cam_back_left_spec['width'] = str(CAMERA_IMAGE_X)
        cam_back_left_spec['height'] = str(CAMERA_IMAGE_Y)
        cam_back_left_spec["fov"] = str(self.cams['FOV_CAM_BACK_LEFT'])
        cam_back_left_spec['id'] = "cam_back_left01"
        cam_back_left_spec['x'], cam_back_left_spec['y'], cam_back_left_spec['z'] = self.cams['T_CAM_BACK_LEFT']
        cam_back_left_spec['roll'], cam_back_left_spec['pitch'], cam_back_left_spec['yaw'] = self.cams['R_CAM_BACK_LEFT']
        cam_back_left_spec['type'] = 'sensor.camera.rgb'
        cam_back_left_spec['motion_blur_intensity'] = 0

        cam_back_right_spec = {}
        cam_back_right_spec['width'] = str(CAMERA_IMAGE_X)
        cam_back_right_spec['height'] = str(CAMERA_IMAGE_Y)
        cam_back_right_spec["fov"] = str(self.cams['FOV_CAM_BACK_RIGHT'])
        cam_back_right_spec['id'] = "cam_back_right01"
        cam_back_right_spec['x'], cam_back_right_spec['y'], cam_back_right_spec['z'] = self.cams['T_CAM_BACK_RIGHT']
        cam_back_right_spec['roll'], cam_back_right_spec['pitch'], cam_back_right_spec['yaw'] = self.cams['R_CAM_BACK_RIGHT']
        cam_back_right_spec['type'] = 'sensor.camera.rgb'
        cam_back_right_spec['motion_blur_intensity'] = 0

        depth_camera_spec = {}
        depth_camera_spec["width"] = str(CAMERA_IMAGE_X)
        depth_camera_spec["height"] = str(CAMERA_IMAGE_Y)
        depth_camera_spec["fov"] = str(90.0)
        depth_camera_spec['id'] = "depth01"
        depth_camera_spec['x'], depth_camera_spec['y'], depth_camera_spec['z'] = 0.0, 0.0, self.lids['GLOBAL_HEIGHT_POS']
        depth_camera_spec['roll'], depth_camera_spec['pitch'], depth_camera_spec['yaw'] = 0.0, 0.0, 0.0
        depth_camera_spec['type'] = "sensor.camera.depth"
        depth_camera_spec['motion_blur_intensity'] = 0

        specs.extend([camera_spec, depth_camera_spec,
                      cam_front_spec, cam_front_left_spec, cam_front_right_spec,
                      cam_back_spec, cam_back_left_spec, cam_back_right_spec])

        return specs


