#!/usr/bin/env python

# This file is modified base on https://github.com/carla-simulator/scenario_runner/blob/master/scenario_runner.py

# Copyright (c) 2018-2020 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
Welcome to CARLA scenario_runner

This is the main script to be executed when running a scenario.
It loads the scenario configuration, loads the scenario and manager,
and finally triggers the scenario execution.
"""

import glob
import traceback
import argparse
from argparse import RawTextHelpFormatter
from datetime import datetime
import importlib
import inspect
import os
import signal
import sys
import time
import json
import numpy as np
import math
import toml
import re

# fill in the following with the absolution paths
sys.path.append(
    "/home/ye/Programs/carla_10/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg"
)
sys.path.append(
    "/home/ye/Programs/carla_10/PythonAPI/carla/agents"
)
sys.path.append(
    "/home/ye/Programs/carla_10/PythonAPI/carla"
)
sys.path.append(
    "/home/ye/Programs/carla_10/PythonAPI"
)
os.environ['CARLA_ROOT'] = '/home/ye/Programs/carla_10'
os.environ['SCENARIO_RUNNER_ROOT'] = '../scenario_runner'


import carla

import py_trees

from constants import *
from kitti_format import KittiDescriptor
from callback import callbackHandler
from lidar import LiDARSetup, Sensor

from srunner.scenarioconfigs.openscenario_configuration import OpenScenarioConfiguration
from srunner.scenariomanager.scenario_manager import ScenarioManager
from srunner.scenarios.open_scenario import OpenScenario
from srunner.scenarios.route_scenario import RouteScenario
from srunner.tools.scenario_parser import ScenarioConfigurationParser
from srunner.tools.route_parser import RouteParser
from srunner.scenariomanager.timer import GameTime
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from utils import *



# Version of scenario_runner, it does not matter to use 0.9.10, ignore this VERSION here
VERSION = "0.9.9"

Translation = namedtuple("Translation", "x y z")
Translation.__new__.__defaults__ = (0.0, 0.0, 0.0)

Rotation = namedtuple("Rotation", "pitch yaw roll")
Rotation.__new__.__defaults__ = (0.0, 0.0, 0.0)

Scale = namedtuple("Scale", "x y z")
Scale.__new__.__defaults__ = (1.0, 1.0, 1.0)


class ScenarioRunner(object):

    """
    This is the core scenario runner module. It is responsible for
    running (and repeating) a single scenario or a list of scenarios.

    Usage:
    scenario_runner = ScenarioRunner(args)
    scenario_runner.run()
    del scenario_runner
    """

    ego_vehicles = []

    # Tunable parameters
    client_timeout = 500.0  # in seconds
    wait_for_world = 50.0  # in seconds
    frame_rate = 20.0  # in Hz

    # CARLA world and scenario handlers
    world = None
    manager = None

    additional_scenario_module = None

    agent_instance = None
    module_agent = None

    def __init__(self, args):
        """
        Setup CARLA client and world
        Setup ScenarioManager
        """
        self.split = args.split
        self.params = toml.load(f"../hyperparams/{args.hyperparams}")
        self.OUTPUT_FOLDER = self.params['paths']['output']
        self.update_paths(args)
        self.first = True
        self._args = args
        create_directories(self, self.split, self._args)
        # self.save_no_1 = get_last_save_no(self, self.split)
        # print(f"Found save_no {self.save_no_1} in {self.OUTPUT_FOLDER}")

        if args.full_round:
            os.makedirs(os.path.join(self.OUTPUT_FOLDER, "logs"), exist_ok=True)

        self.callback = callbackHandler()
        self.sensor_save = False

        self.camera_nos = 0
        self.depth_camera_nos = 0
        self.may_be = 999
        self.pause_index = 999

        if args.timeout:
            self.client_timeout = float(args.timeout)

        self.sensors = []
        # First of all, we need to create the client that will send the requests
        # to the simulator. Here we'll assume the simulator is accepting
        # requests in the localhost at port 2000.
        self.client = carla.Client(args.host, int(args.port))
        # measurements, sensor_data = self.client.read_data()

        k = np.identity(3)
        k[0, 2] = WINDOW_WIDTH_HALF
        k[1, 2] = WINDOW_HEIGHT_HALF
        f = WINDOW_WIDTH / (2.0 * math.tan(90.0 * math.pi / 360.0))
        k[0, 0] = k[1, 1] = f

        self._intrinsic = k
        self._extrinsic = None

        self.client.set_timeout(self.client_timeout)

        self.traffic_manager = self.client.get_trafficmanager(
            int(self._args.trafficManagerPort)
        )

        # Load agent if requested via command line args
        # If something goes wrong an exception will be thrown by importlib (ok here)
        if self._args.agent is not None:
            module_name = os.path.basename(args.agent).split(".")[0]
            sys.path.insert(0, os.path.dirname(args.agent))
            self.module_agent = importlib.import_module(module_name)

        # Create the ScenarioManager
        self.manager = ScenarioManager(
            self._args.debug, self._args.sync, self._args.timeout
        )

        # Create signal handler for SIGINT
        self._shutdown_requested = False
        if sys.platform != "win32":
            signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self._start_wall_time = datetime.now()

    def update_paths(self, args):
        self.GROUNDPLANE_PATH = os.path.join(self.OUTPUT_FOLDER, 'training/planes/15{0:014}.txt')

        self.LIDAR_PATH = []
        self.LIDAR_SEG_PATH = []
        ldv = toml.load(f"../hyperparams/{args.lidar_params}")['lidar']
        cdv = toml.load(f"../hyperparams/{args.lidar_params}")['camera']
        self.CAMERA_HEIGHT_POS = ldv['GLOBAL_HEIGHT_POS']
        self.LIDAR_HEIGHT_POS = ldv['GLOBAL_HEIGHT_POS']

        for p in range(ldv["sets"]):
            self.LIDAR_PATH.append(os.path.join(
                f'../dataset/nus/LiDAR_p{p}_samples/',
                'samples/LIDAR_TOP/n008-2018-08-01-00-00-00-0400__LIDAR_TOP__15{0:014}.pcd.bin'))
            self.LIDAR_SEG_PATH.append(os.path.join(
                f'../dataset/nus/LiDAR_p{p}_samples/', 'lidarseg/v1.0-trainval/3{0:031}_lidarseg.bin'))

        self.LABEL_PATH = os.path.join(self.OUTPUT_FOLDER, 'training/label_2/15{0:014}.txt')
        self.IMAGE_PATH = os.path.join(self.OUTPUT_FOLDER, 'training/image_2/15{0:014}.jpg')
        self.CALIBRATION_PATH = os.path.join(self.OUTPUT_FOLDER, 'training/calib/{0:012}.txt')  # 000100000001.txt
        self.EGO_POSITION_PATH = os.path.join(self.OUTPUT_FOLDER, 'training/position/15{0:014}.txt')
        self.TIMESTAMP_PATH = os.path.join(self.OUTPUT_FOLDER, 'training/timestamp/15{0:014}.txt')

        self.CAM_FRONT_PATH = os.path.join(self.OUTPUT_FOLDER,
                                           'IMAGE/CAM_FRONT/n008-2018-08-01-00-00-00-0400__CAM_FRONT__15{0:014}.jpg')
        self.CAM_FRONT_LEFT_PATH = os.path.join(self.OUTPUT_FOLDER,
                                                'IMAGE/CAM_FRONT_LEFT/n008-2018-08-01-00-00-00-0400__CAM_FRONT_LEFT__15{0:014}.jpg')
        self.CAM_FRONT_RIGHT_PATH = os.path.join(self.OUTPUT_FOLDER,
                                                 'IMAGE/CAM_FRONT_RIGHT/n008-2018-08-01-00-00-00-0400__CAM_FRONT_RIGHT__15{0:014}.jpg')
        self.CAM_BACK_PATH = os.path.join(self.OUTPUT_FOLDER,
                                          'IMAGE/CAM_BACK/n008-2018-08-01-00-00-00-0400__CAM_BACK__15{0:014}.jpg')
        self.CAM_BACK_LEFT_PATH = os.path.join(self.OUTPUT_FOLDER,
                                               'IMAGE/CAM_BACK_LEFT/n008-2018-08-01-00-00-00-0400__CAM_BACK_LEFT__15{0:014}.jpg')
        self.CAM_BACK_RIGHT_PATH = os.path.join(self.OUTPUT_FOLDER,
                                                'IMAGE/CAM_BACK_RIGHT/n008-2018-08-01-00-00-00-0400__CAM_BACK_RIGHT__15{0:014}.jpg')


    def create_transform_matrix(self, transform: carla.Transform):
        print("function 'create_transform_matrix' in 'scenario_runner.py' should not be called, please check the usage")
        matrix = np.identity(4)
        scale = Scale()

        cy = math.cos(np.radians(transform.rotation.yaw))
        sy = math.sin(np.radians(transform.rotation.yaw))
        cr = math.cos(np.radians(transform.rotation.roll))
        sr = math.sin(np.radians(transform.rotation.roll))
        cp = math.cos(np.radians(transform.rotation.pitch))
        sp = math.sin(np.radians(transform.rotation.pitch))
        matrix[0, 3] = transform.location.x
        matrix[1, 3] = transform.location.y
        matrix[2, 3] = transform.location.x
        matrix[0, 0] = scale.x * (cp * cy)
        matrix[0, 1] = scale.y * (cy * sp * sr - sy * cr)
        matrix[0, 2] = -scale.z * (cy * sp * cr + sy * sr)
        matrix[1, 0] = scale.x * (sy * cp)
        matrix[1, 1] = scale.y * (sy * sp * sr + cy * cr)
        matrix[1, 2] = scale.z * (cy * sr - sy * sp * cr)
        matrix[2, 0] = scale.x * (sp)
        matrix[2, 1] = -scale.y * (cp * sr)
        matrix[2, 2] = scale.z * (cp * cr)
        return matrix

    def destroy(self):
        """
        Cleanup and delete actors, ScenarioManager and CARLA world
        """

        self._cleanup()
        if self.manager is not None:
            del self.manager
        if self.world is not None:
            del self.world
        if self.client is not None:
            del self.client
        if len(self.ego_vehicles) > 0:
            self.lidar.destroy()
            self.depth_camera.destroy()
            self.camera.destroy()

    def _signal_handler(self, signum, frame):
        """
        Terminate scenario ticking when receiving a signal interrupt
        """
        self._shutdown_requested = True
        if self.manager:
            self.manager.stop_scenario()
            self._cleanup()
            if not self.manager.get_running_status():
                raise RuntimeError("Timeout occured during scenario execution")

    def _get_scenario_class_or_fail(self, scenario):
        print("function '_get_scenario_class_or_fail' in 'scenario_runner.py' should not be called, please check the usage")
        """
        Get scenario class by scenario name
        If scenario is not supported or not found, exit script
        """

        # Path of all scenario at "srunner/scenarios" folder + the path of the additional scenario argument
        scenarios_list = glob.glob(
            "{}/srunner/scenarios/*.py".format(os.getenv("SCENARIO_RUNNER_ROOT", "./"))
        )
        scenarios_list.append(self._args.additionalScenario)

        for scenario_file in scenarios_list:

            # Get their module
            module_name = os.path.basename(scenario_file).split(".")[0]
            sys.path.insert(0, os.path.dirname(scenario_file))
            scenario_module = importlib.import_module(module_name)

            # And their members of type class
            for member in inspect.getmembers(scenario_module, inspect.isclass):
                if scenario in member:
                    return member[1]

            # Remove unused Python paths
            sys.path.pop(0)

        print("Scenario '{}' not supported ... Exiting".format(scenario))
        sys.exit(-1)

    def _cleanup(self):
        """
        Remove and destroy all actors
        """
        # Stop all the ai controllers
        for ai_controller in self.world.get_actors().filter('controller.ai.walker'):
            ai_controller.stop()
        # Simulation still running and in synchronous mode?
        if self.world is not None and self._args.sync:
            try:
                # Reset to asynchronous mode
                settings = self.world.get_settings()
                settings.synchronous_mode = False
                settings.fixed_delta_seconds = None
                self.world.apply_settings(settings)
            except RuntimeError:
                sys.exit(-1)

        self.manager.cleanup()

        CarlaDataProvider.cleanup()

        for i, _ in enumerate(self.ego_vehicles):
            if self.ego_vehicles[i]:
                if not self._args.waitForEgo:
                    print("Destroying ego vehicle {}".format(self.ego_vehicles[i].id))
                    self.ego_vehicles[i].destroy()
                self.ego_vehicles[i] = None
        self._stop_sensors()
        self.ego_vehicles = []

        if self.agent_instance:
            self.agent_instance.destroy()
            self.agent_instance = None

    def _stop_sensors(self):
        for sensor in self.sensors:
            sensor.stop()

    def _prepare_ego_vehicles(self, ego_vehicles):
        """
        Spawn or update the ego vehicles
        """

        if not self._args.waitForEgo:
            for vehicle in ego_vehicles:
                self.ego_vehicles.append(
                    CarlaDataProvider.request_new_actor(
                        vehicle.model,
                        vehicle.transform,
                        vehicle.rolename,
                        color=vehicle.color,
                        actor_category=vehicle.category,
                    )
                )
        else:
            ego_vehicle_missing = True
            while ego_vehicle_missing:
                self.ego_vehicles = []
                ego_vehicle_missing = False
                for ego_vehicle in ego_vehicles:
                    ego_vehicle_found = False
                    carla_vehicles = (
                        CarlaDataProvider.get_world().get_actors().filter("vehicle.*")
                    )
                    for carla_vehicle in carla_vehicles:
                        if (
                            carla_vehicle.attributes["role_name"]
                            == ego_vehicle.rolename
                        ):
                            ego_vehicle_found = True
                            self.ego_vehicles.append(carla_vehicle)
                            break
                    if not ego_vehicle_found:
                        ego_vehicle_missing = True
                        break

            for i, _ in enumerate(self.ego_vehicles):
                self.ego_vehicles[i].set_transform(ego_vehicles[i].transform)
                CarlaDataProvider.register_actor(self.ego_vehicles[i])

         #sync state
        if CarlaDataProvider.is_sync_mode():
            self.world.tick()
        else:
            self.world.wait_for_tick()

    def setup_transforms(self):
        print("function 'setup_transforms' in 'scenario_runner.py' should not be called, please check the usage")
        k = np.identity(3)
        k[0, 2] = WINDOW_WIDTH_HALF
        k[1, 2] = WINDOW_HEIGHT_HALF
        f = WINDOW_WIDTH / (2.0 * math.tan(90.0 * math.pi / 360.0))
        k[0, 0] = k[1, 1] = f
        self.camera_to_car_transform = self.camera_to_car_transform()
        self.lidar_to_car_transform = self.lidar_to_car_transform()

    def _attach_lidar_to_ego_vehicle(self):
        print("function '_attach_lidar_to_ego_vehicle' in 'scenario_runner.py' should not be called, please check the usage")
        lidar_bp = self.create_lidar(64.0, 1)

        lidar_transform = carla.Transform(
            carla.Location(x=0.0, y=0.0, z=self.LIDAR_HEIGHT_POS)
        )
        self.lidar_to_car_transform = lidar_transform

        self.lidar = self.world.spawn_actor(
            lidar_bp, lidar_transform, attach_to=self.ego_vehicles[0]
        )

        self.sensors.append(self.lidar)
        self.lidar.listen(lambda point_cloud: self.lidar_callback(point_cloud))

    def multiple_lidar_callback(self, points, name):
        print("function 'multiple_lidar_callback' in 'scenario_runner.py' should not be called, please check the usage")
        self.callback(points, name, self.callback.queue)

    def _attach_camera_to_ego_vehicle(self):
        print("function '_attach_camera_to_ego_vehicle' in 'scenario_runner.py' should not be called, please check the usage")
        camera_bp = self.create_camera()

        camera_transform = carla.Transform(
            carla.Location(x=0.0, y=0.0, z=self.CAMERA_HEIGHT_POS)
        )

        self._camera_to_car_transform = camera_transform

        self.camera = self.world.spawn_actor(
            camera_bp, camera_transform, attach_to=self.ego_vehicles[0]
        )

        self.sensors.append(self.camera)
        self.camera.listen(lambda image: self.camera_callback(image))

    def _attach_depth_camera_to_ego_vehicle(self):
        print("function '_attach_depth_camera_to_ego_vehicle' in 'scenario_runner.py' should not be called, please check the usage")
        depth_camera_bp = self.create_depth_camera()

        depth_camera_transform = carla.Transform(
            carla.Location(x=0.0, y=0.0, z=self.CAMERA_HEIGHT_POS)# + user_offset
        )

        self.depth_camera = self.world.spawn_actor(
            depth_camera_bp, depth_camera_transform, attach_to=self.ego_vehicles[0]
        )
        self.sensors.append(self.depth_camera)
        self.depth_camera.listen(lambda image: self.depth_camera_callback(image))

    def lidar_callback(self, point_cloud):
        print("function 'lidar_callback' in 'scenario_runner.py' should not be called, please check the usage")

        if self.first:  # Resolves frame mismatch issue due to spawning time
            self.first = False
            return
        self.lidar_data = point_cloud
        self.queue.put((point_cloud, "lidar01"))


    def camera_callback(self, image):
        print("function 'camera_callback' in 'scenario_runner.py' should not be called, please check the usage")
        self.image = image
        self.callback(image, "cam", self.callback.queue)
        self.image = image
        self.frame = self.image.frame

    def depth_camera_callback(self, depth_image):
        print("function 'depth_camera_callback' in 'scenario_runner.py' should not be called, please check the usage")
        self.depth_image = depth_image
        self.callback(depth_image, "depth01", self.callback.queue)

    def create_depth_camera(self):
        print("function 'create_depth_camera' in 'scenario_runner.py' should not be called, please check the usage")
        self.depth_camera_nos += 1
        print(f"Creating Depth Camera {self.depth_camera_nos}")
        blueprint_library = self.world.get_blueprint_library()
        depth_camera_bp = blueprint_library.find("sensor.camera.depth")
        depth_camera_bp.set_attribute("image_size_x", str(CAMERA_IMAGE_X))
        depth_camera_bp.set_attribute("image_size_y", str(CAMERA_IMAGE_Y))
        depth_camera_bp.set_attribute("fov", str(90.0))
        self.depth_save = False
        return depth_camera_bp

    def create_camera(self):
        print("function 'create_camera' in 'scenario_runner.py' should not be called, please check the usage")
        self.camera_nos += 1
        print(f"Creating Camera {self.camera_nos}")
        blueprint_library = self.world.get_blueprint_library()
        camera_bp = blueprint_library.find("sensor.camera.rgb")
        camera_bp.set_attribute("image_size_x", str(CAMERA_IMAGE_X))
        camera_bp.set_attribute("image_size_y", str(CAMERA_IMAGE_Y))

        self.save = False

        return camera_bp

    def create_lidar(self, channels, no):
        print("function 'create_lidar' in 'scenario_runner.py' should not be called, please check the usage")
        self.lidars_nos += 1
        print(f"Creating LIDAR with channels {channels}")
        blueprint_library = self.world.get_blueprint_library()
        lidar_bp = blueprint_library.find("sensor.lidar.ray_cast")
        lidar_bp.set_attribute("noise_stddev", "0.2")

        lidar_bp.set_attribute("upper_fov", str(5.0))
        lidar_bp.set_attribute("lower_fov", str(-25.0))
        lidar_bp.set_attribute("channels", str(channels))
        lidar_bp.set_attribute("range", str(100.0))
        lidar_bp.set_attribute("rotation_frequency", str(1.0 / 0.1))
        lidar_bp.set_attribute("points_per_second", str(800000))
        self.prev_location = self.vector3d_to_array(
            self.ego_vehicles[0].get_transform().location
        )
        return lidar_bp

    def _check_distance_from_last(self):
        curr_checktime = GameTime.get_time()
        time_interval = curr_checktime - self.prev_checktime

        curr_location = self.primary_vehicle.get_transform().location
        curr_location = self.vector3d_to_array(curr_location)

        yylen = len(self.prev_location)
        if yylen > 41:
            distance = self.distance_arrays(curr_location, self.prev_location[yylen - 40])
        else:
            # distance = self.distance_arrays(curr_location, self.prev_location[0])
            distance = SAVE_DISTANCE + 1

        original_distance = self.distance_arrays(
            curr_location, self.vector3d_to_array(self.original_location)
        )

        if time_interval > SAVE_INTERVAL:
            self.prev_location.append(curr_location)
            self.pause_index += 1
            if distance > SAVE_DISTANCE:
                self.camera_save = True
                self.lidar_save = True
                self.depth_save = True
                self.sensor_save = True
                self.cam_front_save = True
                self.cam_front_left_save = True
                self.cam_front_right_save = True
                self.cam_back_save = True
                self.cam_back_left_save = True
                self.cam_back_right_save = True
                # self.prev_location.append(curr_location)
                self.prev_checktime = curr_checktime
                if self.pause_index == 1:
                    self.save_no = (int(self.save_no / 10_0000) + 1) * 10_0000 + 1
            else:
                self.pause_index = 0

            # with open('output_trajectory.txt', 'a') as text_file:
            #     text_file.write(str(self.prev_location))
            #     text_file.write('\n')
        # else:
        #     self.camera_save = False
        #     self.lidar_save = False
        #     self.depth_save = False
        #     self.sensor_save = False
        #     self.cam_front_save = False
        #     self.cam_front_left_save = False
        #     self.cam_front_right_save = False
        #     self.cam_back_save = False
        #     self.cam_back_left_save = False
        #     self.cam_back_right_save = False


    def should_detect(self, agent):
        print("function 'should_detect' in 'scenario_runner.py' should not be called, please check the usage")
        return True in [
            agent.HasField(class_type.lower()) for class_type in CLASSES_TO_LABEL
        ]

    def distance_arrays(self, array1, array2):
        dx = array1[0] - array2[0]
        dy = array1[1] - array2[1]
        dz = array1[2] - array2[2]

        return np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    def vector3d_to_array(self, vec3d):
        return np.array([vec3d.x, vec3d.y, vec3d.z])

    def _analyze_scenario(self, config):
        print("function '_analyze_scenario' in 'scenario_runner.py' should not be called, please check the usage")
        """
        Provide feedback about success/failure of a scenario
        """
        # Create the filename
        current_time = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        junit_filename = None
        json_filename = None
        config_name = config.name
        if self._args.outputDir != "":
            config_name = os.path.join(self._args.outputDir, config_name)

        if self._args.junit:
            junit_filename = config_name + current_time + ".xml"
        if self._args.json:
            json_filename = config_name + current_time + ".json"
        filename = None
        if self._args.file:
            filename = config_name + current_time + ".txt"

        if not self.manager.analyze_scenario(
            self._args.output, filename, junit_filename, json_filename
        ):
            print("All scenario tests were passed successfully!")
        else:
            print("Not all scenario tests were successful")
            if not (self._args.output or filename or junit_filename):
                print("Please run with --output for further information")

    def _record_criteria(self, criteria, name):
        print("function '_record_criteria' in 'scenario_runner.py' should not be called, please check the usage")
        """
        Filter the JSON serializable attributes of the criterias and
        dumps them into a file. This will be used by the metrics manager,
        in case the user wants specific information about the criterias.
        """
        file_name = name[:-4] + ".json"

        # Filter the attributes that aren't JSON serializable
        with open("temp.json", "w") as fp:

            criteria_dict = {}
            for criterion in criteria:

                criterion_dict = criterion.__dict__
                criteria_dict[criterion.name] = {}

                for key in criterion_dict:
                    if key != "name":
                        try:
                            key_dict = {key: criterion_dict[key]}
                            json.dump(key_dict, fp, sort_keys=False, indent=4)
                            criteria_dict[criterion.name].update(key_dict)
                        except TypeError:
                            pass

        os.remove("temp.json")

        # Save the criteria dictionary into a .json file
        with open(file_name, "w") as fp:
            json.dump(criteria_dict, fp, sort_keys=False, indent=4)

    def _load_and_wait_for_world(self, town, ego_vehicles=None):
        """
        Load a new CARLA world and provide data to CarlaDataProvider
        """

        if self._args.reloadWorld:
            self.world = self.client.load_world(town)
        else:
            ego_vehicle_found = False
            if self._args.waitForEgo:
                while not ego_vehicle_found and not self._shutdown_requested:
                    vehicles = self.client.get_world().get_actors().filter("vehicle.*")
                    for ego_vehicle in ego_vehicles:
                        ego_vehicle_found = False
                        for vehicle in vehicles:
                            if vehicle.attributes["role_name"] == ego_vehicle.rolename:
                                ego_vehicle_found = True
                                break
                        if not ego_vehicle_found:
                            print("Not all ego vehicles ready. Waiting ... ")
                            time.sleep(1)
                            break
                    pedestrians = self.client.get_world().get_actors().filter("*walker*")
                    for ego_vehicle in ego_vehicles:
                        ego_vehicle_found = False
                        for vehicle in pedestrians:
                            if vehicle.attributes["role_name"] == ego_vehicle.rolename:
                                ego_vehicle_found = True
                                break
                        if not ego_vehicle_found:
                            print("Not all ego vehicles ready. Waiting ... ")
                            time.sleep(1)
                            break

        self.world = self.client.get_world()

        if self._args.sync:
            settings = self.world.get_settings()
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = 1.0 / self.frame_rate
            self.world.apply_settings(settings)

            self.traffic_manager.set_synchronous_mode(True)
            self.traffic_manager.set_random_device_seed(
                int(self._args.trafficManagerSeed)
            )

        CarlaDataProvider.set_client(self.client)
        CarlaDataProvider.set_world(self.world)
        CarlaDataProvider.set_traffic_manager_port(int(self._args.trafficManagerPort))

        # Wait for the world to be ready
        if CarlaDataProvider.is_sync_mode():
            self.world.tick()
        else:
            self.world.wait_for_tick()
        if (
            CarlaDataProvider.get_map().name != town
            and CarlaDataProvider.get_map().name != "OpenDriveMap"
        ):
            print(
                "The CARLA server uses the wrong map: {}".format(
                    CarlaDataProvider.get_map().name
                )
            )
            print("This scenario requires to use map: {}".format(town))
            return False

        return True

    def _load_and_run_scenario(self, config):
        """
        Load and run the scenario given by config
        """
        result = False
        if not self._load_and_wait_for_world(config.town, config.ego_vehicles):
            self._cleanup()
            return False

        if self._args.agent:
            agent_class_name = self.module_agent.__name__.title().replace("_", "")
            try:
                self.agent_instance = getattr(self.module_agent, agent_class_name)(
                    self._args.agentConfig
                )
                config.agent = self.agent_instance # some npc agent
            except Exception as e:  # pylint: disable=broad-except
                traceback.print_exc()
                print("Could not setup required agent due to {}".format(e))
                self._cleanup()
                return False

        # Prepare scenario
        print("Preparing scenario: " + config.name)
        print("config.ego_vehicles", config.ego_vehicles)
        try:
            self._prepare_ego_vehicles(config.ego_vehicles)
            if len(self.ego_vehicles) > 0:
                print("len(self.ego_vehicles)>0 in 'load_and_run_scenario' of 'scenario_runner.py' should not be called, please check the usage")
                self.original_location = self.ego_vehicles[0].get_transform().location
                self.lidar = LiDARSetup(
                    self._args.lidar_params,
                    self.world,
                    self.ego_vehicles[0],
                    self.callback,
                    setup=True,
                )

                self.lidars = self.lidar.stats["l"]
                self.lidar_heights = self.lidar.stats["h"]
                self.lidar_transforms = self.lidar.stats["t"]
                self._attach_camera_to_ego_vehicle()
                self._attach_depth_camera_to_ego_vehicle()

                self.primary_vehicle = self.ego_vehicles[0]

            else:
                self.lidar = LiDARSetup(
                    self._args.lidar_params,
                    self.world,
                    self.agent_instance,
                    self.callback,
                    setup=False,
                )
                self.primary_vehicle = self.agent_instance
                self.sensor = Sensor(self._args.lidar_params, self.lidar)

            print(f"Number of ego vehicles {len(self.ego_vehicles)}")
            if self._args.openscenario:
                scenario = OpenScenario(
                    world=self.world,
                    ego_vehicles=self.ego_vehicles,
                    config=config,
                    config_file=self._args.openscenario,
                    timeout=100000,
                )
            elif self._args.route:
                scenario = RouteScenario(
                    world=self.world, config=config, debug_mode=self._args.debug
                )
            else:
                scenario_class = self._get_scenario_class_or_fail(config.type)
                scenario = scenario_class(
                    self.world,
                    self.ego_vehicles,
                    config,
                    self._args.randomize,
                    self._args.debug,
                )
        except Exception as exception:  # pylint: disable=broad-except
            print("The scenario cannot be loaded")
            traceback.print_exc()
            print(exception)
            self._cleanup()
            return False

        try:
            if self._args.record:
                recorder_name = "{}/{}/{}.log".format(
                    os.getenv("SCENARIO_RUNNER_ROOT", "./"),
                    self._args.record,
                    config.name,
                )
                self.client.start_recorder(recorder_name, True)

            # Load scenario and run it

            self.manager.load_scenario(scenario, self.agent_instance, self.sensor.create_sensor_spec())

            self.run_scenario()

            # Provide outputs if required
            self._analyze_scenario(config)

            # Remove all actors, stop the recorder and save all criterias (if needed)
            scenario.remove_all_actors()
            if self._args.record:
                self.client.stop_recorder()
                self._record_criteria(
                    self.manager.scenario.get_criteria(), recorder_name
                )

            result = True

        except Exception as e:  # pylint: disable=broad-except
            traceback.print_exc()
            print(e)
            result = False

        self._cleanup()
        return result

    def to_unreal_matrix(self, matrix):  # , translation, rotation, scale):
        translation = Translation()
        rotation = Rotation(roll=-90, yaw=90)
        scale = Scale(x=-1)
        return np.dot(matrix, self.create_matrix(translation, rotation, scale))

    # def get_camera_to_car_transform_matrix(self):
    #     print("function 'get_camera_to_car_transform_matrix' in 'scenario_runner.py' should not be called, please check the usage")
    #     vehicle_transform = self.ego_vehicles[0].get_transform()
    #
    #     translation = Translation(CAMERA_POS_X, CAMERA_POS_Y, CAMERA_POS_Z)
    #     rotation = Rotation(CAMERA_ROT_PITCH, CAMERA_ROT_YAW, CAMERA_ROT_ROLL)
    #     scale = Scale()
    #
    #     initial_pos_matrix = self.create_matrix(translation, rotation, scale)
    #     unreal_transformed_matrix = self.to_unreal_matrix(initial_pos_matrix)
    #     return unreal_transformed_matrix

    # def lidar_to_car_transform_matrix(self):
    #     print("function 'lidar_to_car_transform_matrix' in 'scenario_runner.py' should not be called, please check the usage")
    #     translation = Translation(LIDAR_POS_X, LIDAR_POS_Y, LIDAR_POS_Z)
    #     rotation = Rotation(LIDAR_ROT_PITCH, LIDAR_ROT_YAW, LIDAR_ROT_ROLL)
    #     scale = Scale()
    #
    #     initial_pos_matrix = self.create_matrix(translation, rotation, scale)
    #     converter = self.create_matrix(Translation(), Rotation(yaw=90), Scale(z=-1))
    #     return np.dot(initial_pos_matrix, converter)

    def create_matrix(self, location, rotation, scale):
        matrix = np.identity(4)

        cy = math.cos(np.radians(rotation.yaw))
        sy = math.sin(np.radians(rotation.yaw))
        cr = math.cos(np.radians(rotation.roll))
        sr = math.sin(np.radians(rotation.roll))
        cp = math.cos(np.radians(rotation.pitch))
        sp = math.sin(np.radians(rotation.pitch))
        matrix[0, 3] = location.x
        matrix[1, 3] = location.y
        matrix[2, 3] = location.x
        matrix[0, 0] = scale.x * (cp * cy)
        matrix[0, 1] = scale.y * (cy * sp * sr - sy * cr)
        matrix[0, 2] = -scale.z * (cy * sp * cr + sy * sr)
        matrix[1, 0] = scale.x * (sy * cp)
        matrix[1, 1] = scale.y * (sy * sp * sr + cy * cr)
        matrix[1, 2] = scale.z * (cy * sr - sy * sp * cr)
        matrix[2, 0] = scale.x * (sp)
        matrix[2, 1] = -scale.y * (cp * sr)
        matrix[2, 2] = scale.z * (cp * cr)
        return matrix

    def _run_scenarios(self):
        print("function '_run_scenarios' in 'scenario_runner.py' should not be called, please check the usage")
        """
        Run conventional scenarios (e.g. implemented using the Python API of ScenarioRunner)
        """
        result = False

        # Load the scenario configurations provided in the config file
        scenario_configurations = (
            ScenarioConfigurationParser.parse_scenario_configuration(
                self._args.scenario, self._args.configFile
            )
        )
        if not scenario_configurations:
            print(
                "Configuration for scenario {} cannot be found!".format(
                    self._args.scenario
                )
            )
            return result

        # Execute each configuration
        for config in scenario_configurations:
            for _ in range(self._args.repetitions):
                result = self._load_and_run_scenario(config)

            self._cleanup()
        return result

    def _run_route(self):
        """
        Run the route scenario
        """
        result = False

        if self._args.route:
            routes = self._args.route[0]
            scenario_file = self._args.route[1]
            single_route = None
            if len(self._args.route) > 2:
                single_route = self._args.route[2]

        # retrieve routes
        route_configurations = RouteParser.parse_routes_file(
            routes, scenario_file, single_route
        )

        for config in route_configurations:
            for _ in range(self._args.repetitions):
                result = self._load_and_run_scenario(config)

                self._cleanup()
        return result

    def _run_openscenario(self):
        print("function '_run_openscenario' in 'scenario_runner.py' should not be called, please check the usage")
        """
        Run a scenario based on OpenSCENARIO
        """

        # Load the scenario configurations provided in the config file
        if not os.path.isfile(self._args.openscenario):
            print("File does not exist")
            self._cleanup()
            return False

        config = OpenScenarioConfiguration(self._args.openscenario, self.client)

        result = self._load_and_run_scenario(config)
        self._cleanup()
        return result

    def run(self):
        """
        Run all scenarios according to provided commandline args
        """
        result = True
        if self._args.openscenario:
            result = self._run_openscenario()
        elif self._args.route:
            result = self._run_route()
        else:
            result = self._run_scenarios()

        print("No more scenarios .... Exiting")
        return result

    def on_render(self):

        # compensate for sensor simulation delay
        self.may_be += 1

        self._check_distance_from_last()
        data = {"image": None, "points": None, "depth": None}

        # Process in every iteration objects from the LiDARs, Camera and the Depth Camera
        # iterations = self.lidar.num + 2

        # if self.sensor_save:
        if self.may_be == 1:
            if len(self.ego_vehicles) > 0:
                print('Error len(self.ego_vehicles) > 0')

            else:
                data = self.ddata
                datapoints = self.ddatapoints
                received_data = self.agent_instance.input_data
                data['image'] = received_data['camera01'][0]
                data['cam_front_image'] = received_data['cam_front01'][0]
                data['cam_front_left_image'] = received_data['cam_front_left01'][0]
                data['cam_front_right_image'] = received_data['cam_front_right01'][0]
                data['cam_back_image'] = received_data['cam_back01'][0]
                data['cam_back_left_image'] = received_data['cam_back_left01'][0]
                data['cam_back_right_image'] = received_data['cam_back_right01'][0]
                data['depth'] = depth_to_array(received_data['depth01'][0]) * 1000
                data['points'] = {}
                for i in range(self.lidar.sets):
                    for j in range(self.lidar.num[i]):
                        data['points'][f'l_{i}{j}'] = received_data[f'l_{i}{j}'][0]

            self.sensor_save = False

            # from math import sin, cos

            # datapoints = self.create_datapoints(data)
            #
            # rotation = self.primary_vehicle.get_transform().rotation
            # pitch, roll, yaw = rotation.pitch, rotation.roll, rotation.yaw
            # # Since measurements are in degrees, convert to radians
            #
            # pitch = degrees_to_radians(pitch)
            # roll = degrees_to_radians(roll)
            # yaw = degrees_to_radians(yaw)
            #
            #
            # # Rotation matrix for pitch
            # rotP = np.array(
            #     [[cos(pitch), 0, sin(pitch)], [0, 1, 0], [-sin(pitch), 0, cos(pitch)]]
            # )
            # # Rotation matrix for roll
            # rotR = np.array(
            #     [[1, 0, 0], [0, cos(roll), -sin(roll)], [0, sin(roll), cos(roll)]]
            # )
            #
            # rotRP = np.matmul(rotR, rotP)
            #
            #
            #
            # if data["points"] is None:
            #     return

            self.process_multilidar_multibeam_data(data, datapoints)

            # sensor save index
            self.camera_save = False
            self.lidar_save = False
            self.depth_save = False
            self.sensor_save = False
            self.cam_front_save = False
            self.cam_front_left_save = False
            self.cam_front_right_save = False
            self.cam_back_save = False
            self.cam_back_left_save = False
            self.cam_back_right_save = False


        if self.sensor_save:
            if len(self.ego_vehicles) > 0:
                print('Error len(self.ego_vehicles) > 0')

            else:
                received_data = self.agent_instance.input_data
                data['image'] = received_data['camera01'][0]
                data['cam_front_image'] = received_data['cam_front01'][0]
                data['cam_front_left_image'] = received_data['cam_front_left01'][0]
                data['cam_front_right_image'] = received_data['cam_front_right01'][0]
                data['cam_back_image'] = received_data['cam_back01'][0]
                data['cam_back_left_image'] = received_data['cam_back_left01'][0]
                data['cam_back_right_image'] = received_data['cam_back_right01'][0]
                data['depth'] = depth_to_array(received_data['depth01'][0]) * 1000
                data['points'] = {}
                for i in range(self.lidar.sets):
                    for j in range(self.lidar.num[i]):
                        data['points'][f'l_{i}{j}'] = received_data[f'l_{i}{j}'][0]

            self.sensor_save = False
            from math import sin, cos

            datapoints = self.create_datapoints(data)

            rotation = self.primary_vehicle.get_transform().rotation
            pitch, roll, yaw = rotation.pitch, rotation.roll, rotation.yaw
            # Since measurements are in degrees, convert to radians

            p_location = self.primary_vehicle.get_transform().location
            p_x, p_y, p_z = p_location.x, p_location.y, p_location.z

            pitch = degrees_to_radians(pitch)
            roll = degrees_to_radians(roll)
            yaw = degrees_to_radians(yaw)

            # Rotation matrix for pitch
            rotP = np.array(
                [[cos(pitch), 0, sin(pitch)], [0, 1, 0], [-sin(pitch), 0, cos(pitch)]]
            )
            # Rotation matrix for roll
            rotR = np.array(
                [[1, 0, 0], [0, cos(roll), -sin(roll)], [0, sin(roll), cos(roll)]]
            )

            rotRP = np.matmul(rotR, rotP)

            # p_position_path = self.EGO_POSITION_PATH.format(self.save_no)

            data['position'] = f'{p_x} {p_y} {p_z} {roll} {pitch} {yaw}'
            data['timestamp'] = str(int((float(GameTime.get_time()) + float(self.no.group()) * 1_000_000) * 1_000_000)
                                    + 1800_0000_0000_0000)

            if data["points"] is None:
                return

            # do not use self.process_multilidar_multibeam_data(data, datapoints) here

            self.ddata = data
            self.ddatapoints = datapoints
            self.may_be = 0

        else:
            if len(self.ego_vehicles) > 0:
                print('Error len(self.ego_vehicles) > 0')
                # for i in range(iterations):
                #     self.callback.get()


    def process_multilidar_multibeam_data(self, data, datapoints):

        points_set = []
        lidar_tags_set = []
        lidar_counts = 0
        for i in range(self.lidar.sets):
            points = []
            lidar_tags = []
            for j in range(self.lidar.num[i]):

                dtype = np.dtype([('floats', 'f4', 4), ('ints', np.uintc, 2)])

                # Read the data into a structured array
                structured_array = np.frombuffer(data["points"][f"l_{i}{j}"].raw_data, dtype=dtype)

                # Convert ints to floats
                # ints_as_floats = structured_array['ints'].astype('f4')

                # Create a new array with everything as floats, maintaining the order
                combined_array = np.empty((len(structured_array), 4), dtype='f4')
                combined_array[:, :4] = structured_array['floats']

                lidar_tag = np.empty((len(structured_array), 1), dtype=np.uint32)

                lidar_tag[:, :] = structured_array['ints'][:, 1:]

                point_cloud = np.copy(np.reshape(combined_array, (int(combined_array.shape[0]), 4))[:, :-1])

                point = np.append(point_cloud, np.ones((point_cloud.shape[0], 1)), axis=1)
                # transform_matrix = self.lidar_transforms[i * self.lidar.num + j].get_matrix()
                transform_matrix = self.lidar_transforms[lidar_counts].get_matrix()

                point_wrt_car = np.dot(transform_matrix, point.T).T  # transfer to world frame
                point = point_wrt_car[:, :-1]

                point[:, 2] -= self.CAMERA_HEIGHT_POS

                points.append(point)
                lidar_tags.append(lidar_tag)

                lidar_counts += 1
                print(lidar_counts)

            points = np.vstack(points)
            lidar_tags = np.vstack(lidar_tags)

            points_set.append(points)
            lidar_tags_set.append(lidar_tags)

        self._save_training_files(data, datapoints, points_set, lidar_tags_set)


    def create_datapoint(self, agent, data, self_vehicle):
        #global visible, unvisible
        if data["image"] is None:
            return None
        _, in_max_limits = get_bbo_coords(self_vehicle, agent, MAX_LIMIT)
        if not in_max_limits:
            return None
        camera_to_world = data["image"].transform
        self._extrinsic = camera_to_world
        self._extrinsic_mat = camera_to_world.get_matrix()

        (
            obj_type,
            agent_transform,
            bbox_transform,
            ext,
            location,
        ) = transforms_from_agent(agent)

        camera_something = np.identity(4)
        self._world_transform = self.primary_vehicle.get_transform()
        self._world_transform_matrix = np.matrix(self._world_transform.get_matrix())

        self._camera_transform_matrix = np.matrix(
            self.manager._agent._sensors_transforms_list['camera01'].get_matrix()
        )

        self._camera_to_car_transform_unreal = self.to_unreal_matrix(
            self._camera_transform_matrix
        )

        self._extrinsic = np.dot(
            self._world_transform_matrix, self._camera_to_car_transform_unreal
        )
        self._world_to_camera_mat = np.linalg.inv(self._extrinsic)

        # Bounding Box

        bbox = agent.bounding_box

        vertices = self.vertices_from_extension(bbox.extent)

        bbox_transform = carla.Transform(bbox.location, bbox.rotation)

        vertices = array_to_location(vertices)

        vs = []

        for vertex in vertices:
            # v = bbox_transform.transform(vertex)
            v = agent_transform.transform(vertex)
            vs.append(v)

        vertices_pos2d = []
        for vertex in vs:
            # Global Vertex to Global Vector
            pos_vector = vertex_vec3d_to_world_vector(vertex)

            # Camera coordinates
            # Global to Camera
            transformed_3d_pos = proj_to_camera(pos_vector, self._extrinsic)

            if obj_type != "Pedestrian":
                 transformed_3d_pos[1] = transformed_3d_pos[1] + ext.z
            # 2d pixel coordinates

            pos2d = proj_to_2d(transformed_3d_pos, self._intrinsic)

            # The actual rendered depth (may be wall or other object instead of vertex)
            vertex_depth = pos2d[2]
            #x_2d, y_2d = WINDOW_WIDTH/2 - pos2d[0], WINDOW_HEIGHT/2 - pos2d[1]
            x_2d, y_2d = pos2d[0], pos2d[1]

            vertices_pos2d.append((y_2d, x_2d, vertex_depth))


        if self._args.full_round:
            num_valid, num_invalid = check_range(vertices_pos2d)
        #else:
        #    visible, unvisible = check_occlusion(
        #        data["image"], vertices_pos2d, data["depth"], True
        #    )

        visible, unvisible = check_occlusion(
            data["image"], vertices_pos2d, data["depth"], True
        )


        midpoint = midpoint_from_agent_location(
            data["image"], location, self._extrinsic, self._intrinsic
        )


        # At least N vertices has to be visible in order to draw bbox
        datapoint = None

        if (
            not self._args.full_round and visible >= MIN_VISIBLE_VERTICES_FOR_RENDER
            and unvisible < MIN_VISIBLE_VERTICES_FOR_RENDER
        ) or (self._args.full_round and num_valid >= MIN_VALID_VERTICES_FOR_RENDER
            and num_invalid < MAX_INVALID_VERTICES_FOR_RENDER):

            legal_pos2d = list(filter(lambda x: x is not None, vertices_pos2d))
            y_coords, x_coords = [int(x[0][0]) for x in legal_pos2d], [int(x[1][0]) for x in legal_pos2d]
            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)

            if min_x < 0:
                min_x = 0
            if min_y < 0:
                min_y = 0
            if max_x > CAMERA_IMAGE_X:
                max_x = CAMERA_IMAGE_X
            if max_y > CAMERA_IMAGE_Y:
                max_y = CAMERA_IMAGE_Y

            left = CAMERA_IMAGE_X - max_x
            top = CAMERA_IMAGE_Y - max_y
            right = CAMERA_IMAGE_X - min_x
            down = CAMERA_IMAGE_Y - min_y

            bbox_2d = [left, top, right, down]

            if not self._args.full_round:
                bbox_2d = calc_projected_2d_bbox(vertices_pos2d)
                area = calc_bbox2d_area(bbox_2d)
                if area < MIN_BBOX_AREA_IN_PX:
                    return None

            from math import pi

            rotation_y = (
                get_relative_rotation_y(
                    agent.get_transform().rotation.yaw,
                    self.primary_vehicle.get_transform().rotation.yaw,
                )
                % pi
            )

            r = math.sqrt(math.pow(midpoint[0], 2) + math.pow(midpoint[2], 2))
            theta = math.acos(-midpoint[0] / r)
            alpha = - theta + rotation_y

            rotation_y = - pi / 2 + rotation_y

            truncated = unvisible / 8

            if visible >= 6:
                occluded = 0
            elif visible >= 4:
                occluded = 1
            elif visible >= 1:
                occluded = 2
            else:
                occluded = 3

            instance_id = agent.id

            velocity = agent.get_velocity()
            speed = math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)

            datapoint = KittiDescriptor()
            datapoint.set_occlusion(occluded)
            datapoint.set_truncated(truncated)
            datapoint.set_alpha(alpha)
            datapoint.set_bbox(bbox_2d)
            datapoint.set_3d_object_dimensions(ext)
            datapoint.set_type(obj_type)
            datapoint.set_3d_object_location(midpoint)
            datapoint.set_rotation_y(rotation_y)
            datapoint.set_instance(instance_id)
            datapoint.set_speed(speed)

        return datapoint

    def vertices_from_extension(self, ext):
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

    def create_datapoints(self, data):
        pedestrian_data_path = self.params['occupancy']['path'] + "/pedestrian"
        vehicle_data_path = self.params['occupancy']['path'] + "/vehicle"
        bus_data_path = self.params['occupancy']['path'] + "/bus"
        truck_data_path = self.params['occupancy']['path'] + "/truck"
        bicycle_data_path = self.params['occupancy']['path'] + "/bicycle"
        motorcycle_data_path = self.params['occupancy']['path'] + "/motorcycle"
        
        os.makedirs(pedestrian_data_path, exist_ok=True)
        os.makedirs(vehicle_data_path, exist_ok=True)
        os.makedirs(truck_data_path, exist_ok=True)
        os.makedirs(bus_data_path, exist_ok=True)
        os.makedirs(bicycle_data_path, exist_ok=True)
        os.makedirs(motorcycle_data_path, exist_ok=True)
        datapoints = []

        rotRP = np.identity(3)
        actor_list = self.world.get_actors()

        vehicle = self.primary_vehicle

        for actor in actor_list.filter("*vehicle*"):
            if actor.id != vehicle.id:
                # bicycle
                if ("diamondback.century" in actor.type_id
                        or "bh.crossbike" in actor.type_id
                        or "gazelle.omafiets" in actor.type_id):
                    datapoint = self.create_datapoint(actor, data, vehicle)
                    bbox, _ = get_bbo_coords(vehicle, actor)
                    if datapoint:
                        datapoints.append(datapoint)
                    if bbox is not None:
                        np.save(f"{bicycle_data_path}/{actor.id}_{self.save_no}.npy", bbox)  # todo visualize and check

                # motorcycle
                elif ("harley-davidson.low_rider" in actor.type_id
                        or "kawasaki.ninja" in actor.type_id
                        or "vespa.zx125" in actor.type_id
                        or "yamaha.yzf" in actor.type_id):
                    datapoint = self.create_datapoint(actor, data, vehicle)
                    bbox, _ = get_bbo_coords(vehicle, actor)
                    if datapoint:
                        datapoints.append(datapoint)
                    if bbox is not None:
                        np.save(f"{motorcycle_data_path}/{actor.id}_{self.save_no}.npy", bbox)  # todo visualize and check

                # bus
                elif ("mitsubishi.fusorosa" in actor.type_id
                      or "volkswagen.t2_2021" in actor.type_id
                      or "volkswagen.t2" in actor.type_id
                      or "mercedes.sprinter" in actor.type_id
                      or "ford.ambulance" in actor.type_id):
                    datapoint = self.create_datapoint(actor, data, vehicle)
                    bbox, _ = get_bbo_coords(vehicle, actor)
                    if datapoint:
                        datapoints.append(datapoint)
                    if bbox is not None:
                        np.save(f"{bus_data_path}/{actor.id}_{self.save_no}.npy", bbox)  # todo visualize and check

                # truck
                elif ("tesla.cybertruck" in actor.type_id
                      or "carlamotors.firetruck" in actor.type_id
                      or "carlamotors.european_hgv" in actor.type_id
                      or "carlamotors.carlacola" in actor.type_id):
                    datapoint = self.create_datapoint(actor, data, vehicle)
                    bbox, _ = get_bbo_coords(vehicle, actor)
                    if datapoint:
                        datapoints.append(datapoint)
                    if bbox is not None:
                        np.save(f"{truck_data_path}/{actor.id}_{self.save_no}.npy", bbox) # todo visualize and check

                # vehicle
                else:
                    datapoint = self.create_datapoint(actor, data, vehicle)
                    bbox, _ = get_bbo_coords(vehicle, actor)
                    if datapoint:
                        datapoints.append(datapoint)
                    if bbox is not None:
                        np.save(f"{vehicle_data_path}/{actor.id}_{self.save_no}.npy", bbox)

        # pedestrian
        for actor in actor_list.filter("*pedestrian*"):
            if actor.id != vehicle.id:
                datapoint = self.create_datapoint(actor, data, vehicle)
                bbox, _ = get_bbo_coords(vehicle, actor)
                if datapoint:
                    datapoints.append(datapoint)
                if bbox is not None:
                    np.save(
                        f"{pedestrian_data_path}/{actor.id}_{self.save_no}.npy", bbox
                    )
        return datapoints

    def _save_training_files_with_beam(self, image, datapoints, points):
        print("function '_save_training_files_with_beam' in 'scenario_runner.py' should not be called, please check the usage")
        if len(datapoints) > 0:
            groundplane_fname = self.GROUNDPLANE_PATH.format(self.split, self.save_no)

            kitti_fname = self.LABEL_PATH.format(self.split, self.save_no)
            img_fname = self.IMAGE_PATH.format(self.split, self.save_no)
            calib_filename = self.CALIBRATION_PATH.format(self.split, self.save_no)

            save_groundplanes(
                groundplane_fname,
                self.primary_vehicle.get_transform(),
                self.LIDAR_HEIGHT_POS,
            )

            save_kitti_data(kitti_fname, datapoints)
            save_calibration_matrices(calib_filename, self._intrinsic, self._extrinsic)
            save_image_data(img_fname, to_rgb_array(image))

            for beam in points.keys():
                point_cloud = points[beam]

                lidar_fname = self.LIDAR_BEAM_PATH.format(self.split, self.save_no, beam)
                save_lidar_data(lidar_fname, point_cloud, self.LIDAR_HEIGHT_POS, "bin")

    def _save_training_files(self, data, datapoints, point_cloud, lidar_tags, i=None):
        # if CarlaDataProvider.is_sync_mode():

        # if i is not None:
        #     lidar_fname = self.LIDAR_PATH.format(self.save_no*10+i)
        #     save_lidar_data(lidar_fname, point_cloud, self.LIDAR_HEIGHT_POS, "bin")
        #     # save_lidarseg_tags(lidarseg_fname, lidar_tags, "bin")
        #     return
        if len(datapoints) > 0:
            if self.save_no % 40 == 0:
                self.scene_of_this_route += 1

            p_position_path = self.EGO_POSITION_PATH.format(self.save_no)
            with open(p_position_path, 'w') as file:
                file.write(data['position'])

            t_timestamp_path = self.TIMESTAMP_PATH.format(self.save_no)
            with open(t_timestamp_path, 'w') as file:
                file.write(data['timestamp'])

            groundplane_fname = self.GROUNDPLANE_PATH.format(self.save_no)

            kitti_fname = self.LABEL_PATH.format(self.save_no)

            cam_front_fname = self.CAM_FRONT_PATH.format(self.save_no)
            cam_front_left_fname = self.CAM_FRONT_LEFT_PATH.format(self.save_no)
            cam_front_right_fname = self.CAM_FRONT_RIGHT_PATH.format(self.save_no)
            cam_back_fname = self.CAM_BACK_PATH.format(self.save_no)
            cam_back_left_fname = self.CAM_BACK_LEFT_PATH.format(self.save_no)
            cam_back_right_fname = self.CAM_BACK_RIGHT_PATH.format(self.save_no)

            calib_filename = self.CALIBRATION_PATH.format(self.save_no)

            lidar_frame = []
            lidarseg_frame = []

            for i_frame in range(self.lidar.sets):
                lidar_frame.append(self.LIDAR_PATH[i_frame].format(self.save_no))
                lidarseg_frame.append(self.LIDAR_SEG_PATH[i_frame].format(self.save_no))

            save_groundplanes(
                groundplane_fname,
                self.primary_vehicle.get_transform(),
                self.LIDAR_HEIGHT_POS)

            save_ref_files(self.OUTPUT_FOLDER, self.save_no)
            save_kitti_data(kitti_fname, datapoints)

            save_image_data(cam_front_fname, to_rgb_array(data["cam_front_image"]))
            save_image_data(cam_front_left_fname, to_rgb_array(data["cam_front_left_image"]))
            save_image_data(cam_front_right_fname, to_rgb_array(data["cam_front_right_image"]))
            save_image_data(cam_back_fname, to_rgb_array(data["cam_back_image"]))
            save_image_data(cam_back_left_fname, to_rgb_array(data["cam_back_left_image"]))
            save_image_data(cam_back_right_fname, to_rgb_array(data["cam_back_right_image"]))

            data["cam_front_image"], data["cam_front_left_image"], data["cam_front_right_image"], \
                data["cam_back_image"], data["cam_back_left_image"], data["cam_back_right_image"], \
                data["points"], data["depth"], data["image"] = None, None, None, None, None, None, None, None, None

            for i_f in range(self.lidar.sets):
                save_lidar_data(lidar_frame[i_f], point_cloud[i_f], self.LIDAR_HEIGHT_POS, "bin")
                save_lidarseg_tags(lidarseg_frame[i_f], lidar_tags[i_f], "bin")

            save_calibration_matrices(calib_filename, self._intrinsic, self._extrinsic)
            self.save_no += 1


    def run_scenario(self):
        """
        Trigger the start of the scenario and wait for it to finish/fail
        """
        print(
            "ScenarioManager: Running scenario {}".format(
                self.manager.scenario_tree.name
            )
        )
        self.manager.start_system_time = time.time()
        start_game_time = GameTime.get_time()

        self.manager._watchdog.start()
        self.manager._running = True
        first = True

        while self.manager._running:
            timestamp = None
            world = CarlaDataProvider.get_world()
            if world:
                snapshot = world.get_snapshot()
                if snapshot:
                    timestamp = snapshot.timestamp
            if timestamp:
                self.manager._tick_scenario(timestamp)
                if first:
                    if len(self.ego_vehicles) > 0:
                        self.primary_vehicle = self.ego_vehicles[0]
                    else:
                        self.primary_vehicle = self.agent_instance._agent._vehicle
                    self.original_location = self.primary_vehicle.get_transform().location

                    self.prev_location = []
                    self.prev_location.append(self.vector3d_to_array(self.original_location))

                    self.prev_checktime = GameTime.get_time()
                    self.lidar_transforms, self.lidar_heights = [], []
                    for key in self.manager._agent._sensors_transforms_list.keys():
                        if key[0] == 'l':
                            self.lidar_transforms.append(self.manager._agent._sensors_transforms_list[key])
                            self.lidar_heights.append(self.manager._agent._sensor_heights[key])

                    self.no = re.search(r'\d+', self.manager.scenario_tree.name)
                    self.save_no = int(self.no.group()) * 1_0000_0000 + 1

                    first = False

                    self.scene_of_this_route = 0

                #if self._sync_mode and self._running and self._watchdog.get_status():
                CarlaDataProvider.get_world().tick()

                self.on_render()

                if self.scene_of_this_route == 8:
                    print(f'Finish collecting route {self.no.group()}')
                    break

        self.manager._watchdog.stop()

        self.manager.cleanup()

        self.manager.end_system_time = time.time()
        end_game_time = GameTime.get_time()

        self.manager.scenario_duration_system = (
            self.manager.end_system_time - self.manager.start_system_time
        )
        self.manager.scenario_duration_game = end_game_time - start_game_time

        if self.manager.scenario_tree.status == py_trees.common.Status.FAILURE:
            print("ScenarioManager: Terminated due to failure")




VEHICLE_SAVED = 0
PEDESTRIAN_SAVED = 0


def create_bb_points(vehicle: carla.Vehicle):
    """
    Returns 3D bounding box for a vehicle.
    """

    coords = np.zeros((8, 4))
    extent = vehicle.bounding_box.extent
    coords[0, :] = np.array([extent.x, extent.y, -extent.z, 1])
    coords[1, :] = np.array([-extent.x, extent.y, -extent.z, 1])
    coords[2, :] = np.array([-extent.x, -extent.y, -extent.z, 1])
    coords[3, :] = np.array([extent.x, -extent.y, -extent.z, 1])
    coords[4, :] = np.array([extent.x, extent.y, extent.z, 1])
    coords[5, :] = np.array([-extent.x, extent.y, extent.z, 1])
    coords[6, :] = np.array([-extent.x, -extent.y, extent.z, 1])
    coords[7, :] = np.array([extent.x, -extent.y, extent.z, 1])
    return coords


def get_vehicle_world_coords(vehicle: carla.Vehicle, coords: np.ndarray):
    bbox_vehicle_matrix = carla.Transform(
        vehicle.bounding_box.location, vehicle.bounding_box.rotation
    ).get_matrix()
    vehicle_world_matrix = vehicle.get_transform().get_matrix()
    bb_world_matrix = np.dot(vehicle_world_matrix, bbox_vehicle_matrix)
    world_coords = np.dot(bb_world_matrix, coords.T)
    return world_coords


def bbox_ego_coords(ego_vehicle: carla.Vehicle, coords: np.ndarray):
    """
    Transforms world coordinates to sensor.
    """

    ego_world_matrix = ego_vehicle.get_transform().get_matrix()
    world_ego_matrix = np.linalg.inv(ego_world_matrix)
    ego_coords = np.dot(world_ego_matrix, coords)
    return ego_coords


def in_roi(bbox: np.ndarray, limits: np.ndarray):
    """
    bbox: Bounding Box Coordinates. Shape (4, 8) [X, Y, Z, 1]
    limits: ROI Limit. Shape (2, 3) [[Xmin, Xmax], ...]
    """

    bbox_1 = np.logical_and(bbox[0, :] > limits[0, 0], bbox[0, :] < limits[0, 1])
    bbox_2 = np.logical_and(bbox[1, :] > limits[1, 0], bbox[1, :] < limits[1, 1])
    bbox_3 = np.logical_and(bbox[2, :] > limits[2, 0], bbox[2, :] < limits[2, 1])

    b0 = bbox[0, 0] * bbox[0, 0] + bbox[1, 0] * bbox[1, 0] + bbox[2, 0] * bbox[2, 0]
    b1 = bbox[0, 1] * bbox[0, 1] + bbox[1, 1] * bbox[1, 1] + bbox[2, 1] * bbox[2, 1]
    b2 = bbox[0, 2] * bbox[0, 2] + bbox[1, 2] * bbox[1, 2] + bbox[2, 2] * bbox[2, 2]
    b3 = bbox[0, 3] * bbox[0, 3] + bbox[1, 3] * bbox[1, 3] + bbox[2, 3] * bbox[2, 3]
    b4 = bbox[0, 4] * bbox[0, 4] + bbox[1, 4] * bbox[1, 4] + bbox[2, 4] * bbox[2, 4]
    b5 = bbox[0, 5] * bbox[0, 5] + bbox[1, 5] * bbox[1, 5] + bbox[2, 5] * bbox[2, 5]
    b6 = bbox[0, 6] * bbox[0, 6] + bbox[1, 6] * bbox[1, 6] + bbox[2, 6] * bbox[2, 6]
    b7 = bbox[0, 7] * bbox[0, 7] + bbox[1, 7] * bbox[1, 7] + bbox[2, 7] * bbox[2, 7]

    # if np.any(bbox_1 & bbox_2 & bbox_3):
    #     return True
    if min(b0, b1, b2, b3, b4, b5, b6, b7) < float(MAX_RENDER_DEPTH_IN_METERS * MAX_RENDER_DEPTH_IN_METERS):
        return True
    else:
        return False


def get_bbo_coords(ego: carla.Vehicle, vehicle: carla.Vehicle, range_limit=LIMITS):
    bbox = create_bb_points(vehicle)
    bbox_world = get_vehicle_world_coords(vehicle, bbox)
    bbox_wrt_ego = bbox_ego_coords(ego, bbox_world)

    if in_roi(bbox_wrt_ego, range_limit):
        return bbox_wrt_ego, True
    else:
        return None, False


def main():
    """
    main function
    """
    description = (
        "CARLA Scenario Runner: Setup, Run and Evaluate scenarios using CARLA\n"
        "Current version: " + VERSION
    )

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser(
        description=description, formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + VERSION
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="IP of the host server (default: localhost)"
    )
    parser.add_argument(
        "--port", default="2000", help="TCP port to listen to (default: 2000)"
    )
    parser.add_argument(
        "--timeout",
        default="3600.0",
        help="Set the CARLA client timeout value in seconds",
    )
    parser.add_argument(
        "--trafficManagerPort",
        default="8000",
        help="Port to use for the TrafficManager (default: 8000)",
    )
    parser.add_argument(
        "--trafficManagerSeed",
        default="0",
        help="Seed used by the TrafficManager (default: 0)",
    )
    parser.add_argument(
        "--sync", action="store_true", help="Forces the simulation to run synchronously"
    )
    parser.add_argument(
        "--list", action="store_true", help="List all supported scenarios and exit"
    )

    parser.add_argument(
        "--scenario",
        help="Name of the scenario to be executed. Use the preposition 'group:' to run all scenarios of one class, e.g. ControlLoss or FollowLeadingVehicle",
    )
    parser.add_argument("--openscenario", help="Provide an OpenSCENARIO definition")
    parser.add_argument(
        "--route",
        help="Run a route as a scenario (input: (route_file,scenario_file,[route id]))",
        nargs="+",
        type=str,
    )

    parser.add_argument(
        "--agent",
        help="Agent used to execute the scenario. Currently only compatible with route-based scenarios.",
    )
    parser.add_argument(
        "--agentConfig", type=str, help="Path to Agent's configuration file", default=""
    )

    parser.add_argument(
        "--output", action="store_true", help="Provide results on stdout"
    )
    parser.add_argument(
        "--file", action="store_true", help="Write results into a txt file"
    )
    parser.add_argument(
        "--junit", action="store_true", help="Write results into a junit file"
    )
    parser.add_argument(
        "--json", action="store_true", help="Write results into a JSON file"
    )
    parser.add_argument(
        "--outputDir",
        default="",
        help="Directory for output files (default: this directory)",
    )

    parser.add_argument(
        "--configFile",
        default="",
        help="Provide an additional scenario configuration file (*.xml)",
    )
    parser.add_argument(
        "--additionalScenario",
        default="",
        help="Provide additional scenario implementations (*.py)",
    )

    parser.add_argument("--debug", action="store_true", help="Run with debug output")
    parser.add_argument(
        "--reloadWorld",
        action="store_true",
        help="Reload the CARLA world before starting a scenario (default=True)",
    )
    parser.add_argument(
        "--record",
        type=str,
        default="",
        help="Path were the files will be saved, relative to SCENARIO_RUNNER_ROOT.\nActivates the CARLA recording feature and saves to file all the criteria information.",
    )
    parser.add_argument(
        "--randomize", action="store_true", help="Scenario parameters are randomized"
    )
    parser.add_argument(
        "--repetitions", default=1, type=int, help="Number of scenario executions"
    )
    parser.add_argument(
        "--waitForEgo",
        action="store_true",
        help="Connect the scenario to an existing ego vehicle",
    )

    parser.add_argument(
        "--speed", type=int, default=20, help="Set speed of ego vehicle"
    )

    parser.add_argument(
        "--multilidar", action="store_true", help="Enable multiple LIDARs"
    )

    parser.add_argument(
        "--hyperparams",
        type=str,
        default="../hyperparams/hyper_square.toml",
        help="Path to hyperparameter configuration file",
    )
    parser.add_argument("--split", type=str, default="training", help="Which split?")
    parser.add_argument(
        "--lidar-params", type=str, help="Path to LiDAR Setup Parameters", default=None
    )
    parser.add_argument(
        "--full_round", action="store_true", help="collect objects in 360 degree"
    )
    arguments = parser.parse_args()

    if arguments.list:
        print("Currently the following scenarios are supported:")
        print(
            *ScenarioConfigurationParser.get_list_of_scenarios(arguments.configFile),
            sep="\n",
        )
        return 1

    if not arguments.scenario and not arguments.openscenario and not arguments.route:
        print("Please specify either a scenario or use the route mode\n\n")
        parser.print_help(sys.stdout)
        return 1

    if arguments.route and (arguments.openscenario or arguments.scenario):
        print(
            "The route mode cannot be used together with a scenario (incl. OpenSCENARIO)'\n\n"
        )
        parser.print_help(sys.stdout)
        return 1

    if arguments.agent and (arguments.openscenario or arguments.scenario):
        print("Agents are currently only compatible with route scenarios'\n\n")
        parser.print_help(sys.stdout)
        return 1

    if arguments.route:
        arguments.reloadWorld = True

    if arguments.agent:
        arguments.sync = True

    scenario_runner = None
    result = True
    try:
        scenario_runner = ScenarioRunner(arguments)
        result = scenario_runner.run()

    finally:
        if scenario_runner is not None:
            scenario_runner.destroy()
            del scenario_runner
    return not result


if __name__ == "__main__":
    sys.exit(main())
