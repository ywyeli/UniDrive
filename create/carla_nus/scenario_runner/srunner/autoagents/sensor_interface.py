#!/usr/bin/env python

# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
This file containts CallBack class and SensorInterface, responsible of
handling the use of sensors for the agents
"""

import copy
import logging

try:
    from queue import Queue
    from queue import Empty
except ImportError:
    from Queue import Queue
    from Queue import Empty

import numpy as np

import carla


class SensorReceivedNoData(Exception):

    """
    Exceptions thrown when the sensors used by the agent take too long to receive data
    """


class CallBack(object):

    """
    Class the sensors listen to in order to receive their data each frame
    """

    def __init__(self, tag, sensor, data_provider):
        """
        Initializes the call back
        """
        self._tag = tag
        self._data_provider = data_provider

        self._data_provider.register_sensor(tag, sensor)

    def __call__(self, data):
        """
        call function
        """
        if isinstance(data, carla.Image):
            self._parse_image_cb(data, self._tag)
        elif isinstance(data, carla.LidarMeasurement):
            self._parse_lidar_cb(data, self._tag)
        elif isinstance(data, carla.RadarMeasurement):
            self._parse_radar_cb(data, self._tag)
        elif isinstance(data, carla.GnssMeasurement):
            self._parse_gnss_cb(data, self._tag)
        elif isinstance(data, carla.IMUMeasurement):
            self._parse_imu_cb(data, self._tag)
        elif isinstance(data, carla.SemanticLidarMeasurement):
            self._parse_semantic_lidar_cb(data, self._tag)
        else:
            logging.error('No callback method for this sensor.')

    # Parsing CARLA physical Sensors
    def _parse_image_cb(self, image, tag):
        """
        parses cameras
        """
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = copy.deepcopy(array)
        array = np.reshape(array, (image.height, image.width, 4))
        self._data_provider.update_sensor(tag, array, image)

    def _parse_lidar_cb(self, lidar_data, tag):
        """
        parses lidar sensors
        """
        points = np.frombuffer(lidar_data.raw_data, dtype=np.dtype('f4'))
        points = copy.deepcopy(points)
        points = np.reshape(points, (int(points.shape[0] / 4), 4))
        self._data_provider.update_sensor(tag, points, lidar_data)

    def _parse_semantic_lidar_cb(self, lidar_data, tag):
        """
        parses lidar sensors
        """
        # d_type = np.dtype([('x', np.float32, 1), ('y', np.float32, 1), ('z', np.float32, 1), ('cos', np.float32, 1),
        #                    ('ints', np.int32, 1), ('id', np.int32, 1)])
        # points = np.frombuffer(lidar_data.raw_data, dtype=d_type)
        # points = copy.deepcopy(points)
        # points = [list(tup) for tup in points]
        # points = np.array(points)
        # points = np.reshape(points, (int(points.shape[0] / 6), 6))
        # self._data_provider.update_sensor(tag, points, lidar_data.frame)
        # self._data_provider.update_sensor(tag, points, lidar_data)

        d_type = np.dtype([('floats', 'f4', 4), ('ints', 'i4', 2)])

        # Read the data into a structured array
        structured_array = np.frombuffer(lidar_data.raw_data, dtype=d_type)

        # Convert ints to floats
        # ints_as_floats = structured_array['ints'].astype('f4')

        # Create a new array with everything as floats, maintaining the order
        combined_array = np.empty((len(structured_array), 4), dtype='f4')
        combined_array[:, :4] = structured_array['floats']
        # combined_array[:, 4:] = ints_as_floats

        # Flatten the array and convert to a list to get the final sequence
        # final_sequence = combined_array.ravel().tolist()

        self._data_provider.update_sensor(tag, combined_array, lidar_data)

    def _parse_radar_cb(self, radar_data, tag):
        """
        parses radar sensors
        """
        # [depth, azimuth, altitute, velocity]
        points = np.frombuffer(radar_data.raw_data, dtype=np.dtype('f4'))
        points = copy.deepcopy(points)
        points = np.reshape(points, (int(points.shape[0] / 4), 4))
        points = np.flip(points, 1)
        self._data_provider.update_sensor(tag, points, radar_data.frame)

    def _parse_gnss_cb(self, gnss_data, tag):
        """
        parses gnss sensors
        """
        array = np.array([gnss_data.latitude,
                          gnss_data.longitude,
                          gnss_data.altitude], dtype=np.float64)
        self._data_provider.update_sensor(tag, array, gnss_data.frame)

    def _parse_imu_cb(self, imu_data, tag):
        """
        parses IMU sensors
        """
        array = np.array([imu_data.accelerometer.x,
                          imu_data.accelerometer.y,
                          imu_data.accelerometer.z,
                          imu_data.gyroscope.x,
                          imu_data.gyroscope.y,
                          imu_data.gyroscope.z,
                          imu_data.compass,
                          ], dtype=np.float64)
        self._data_provider.update_sensor(tag, array, imu_data.frame)


class SensorInterface(object):

    """
    Class that contains all sensor data
    """

    def __init__(self):
        """
        Initializes the class
        """
        self._sensors_objects = {}
        self._new_data_buffers = Queue()
        self._queue_timeout = 50

    def register_sensor(self, tag, sensor):
        """
        Registers the sensors
        """
        if tag in self._sensors_objects:
            raise ValueError("Duplicated sensor tag [{}]".format(tag))

        self._sensors_objects[tag] = sensor

    def update_sensor(self, tag, data, timestamp):
        """
        Updates the sensor
        """
        if tag not in self._sensors_objects:
            raise ValueError("The sensor with tag [{}] has not been created!".format(tag))

        self._new_data_buffers.put((tag, timestamp, data))

    def get_data(self):
        """
        Returns the data of a sensor
        """
        try:
            data_dict = {}
            while len(data_dict.keys()) < len(self._sensors_objects.keys()):
                sensor_data = self._new_data_buffers.get(True, self._queue_timeout)
                #print(sensor_data)
                data_dict[sensor_data[0]] = ((sensor_data[1], sensor_data[2]))

        except Empty:
            raise SensorReceivedNoData("A sensor took too long to send its data")

        return data_dict
