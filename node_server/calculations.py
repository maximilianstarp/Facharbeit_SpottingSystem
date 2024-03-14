# import libraries
import json
import numpy as np
import pandas as pd
import requests
from functools import lru_cache

@lru_cache
class DMXCalculator:
    """
    A class for calculating DMX universe based on camera and moving head positions.
    """

    def __init__(self) -> None:
        """
        Initializes the DMXCalculator class with default camera and universe settings.
        """
        self.camera_pan_imag = 180
        self.camera_tilt_imag = 90
        self.universe = [0]*512
    
    def get_distance(self, camera_ip: str, camera_port: int) -> str:
        """
        Retrieves distance information from a camera.
        
        Args:
            camera_ip (str): The IP address of the camera.
            camera_port (int): The port number of the camera.
        
        Returns:
            str: The distance obtained from the camera.
        """
        try:
            distance = int(requests.get(f"http://{camera_ip}:{camera_port}", timeout=0.5).json())
            return distance
        except:
            return None
    
    def calculate_dmx_universe(self, values, shows_data):
        """
        Calculates the DMX universe based on input values and show data.
        
        Args:
            values: The input values.
            shows_data: The show data.
        
        Returns:
            tuple: A tuple containing the DMX universe, distance, coordinates, and angles.
        """
        distance = self.get_distance(camera_ip=shows_data["ip_cam"], camera_port=shows_data["port_cam"])
        parsed_data = json.loads(pd.DataFrame({"values": values})["values"].iloc[0])

        try:
            if distance == None: return[], "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found"

            vector_lamp = np.array([shows_data["xdist"], shows_data["ydist"], shows_data["zdist"]], dtype=float)

            self.camera_pan_imag += float(parsed_data["Axis 0"]) * float(parsed_data["speed"]) / 2 * (-1)
            self.camera_tilt_imag += float(parsed_data["Axis 1"]) * float(parsed_data["speed"]) / 2 * (-1)

            if self.camera_pan_imag <= 0: self.camera_pan_imag = 0
            if self.camera_tilt_imag <= -50: self.camera_tilt_imag = -50
            if self.camera_pan_imag >= 520: self.camera_pan_imag = 520
            if self.camera_tilt_imag >= 230: self.camera_tilt_imag = 230

            # x = distance * np.cos(np.deg2rad(self.camera_tilt_imag)) * np.cos(np.deg2rad(self.camera_pan_imag))
            # y = distance * np.cos(np.deg2rad(self.camera_tilt_imag)) * np.sin(np.deg2rad(self.camera_pan_imag))
            # z = distance * np.sin(np.deg2rad(self.camera_tilt_imag))

            z = distance * np.sin(np.deg2rad(self.camera_tilt_imag))
            x = np.sqrt(distance**2 - z**2) * np.cos(np.deg2rad(self.camera_pan_imag))
            y = np.sqrt(distance**2 - z**2 - x **2)

            vector_point = np.array([x,y,z], dtype=float)
            direction_vector_lamp_point = vector_point - vector_lamp
            direction_vector_lamp_point_normalized = np.linalg.norm(direction_vector_lamp_point)
            movinghead_tilt_imag = 90-np.rad2deg(np.arccos(direction_vector_lamp_point[2]/direction_vector_lamp_point_normalized)) + int(shows_data["tiltrot"])

            vector_xy_plane = [direction_vector_lamp_point[0], direction_vector_lamp_point[1], 0]
            vector_xy_plane_sum = np.linalg.norm(vector_xy_plane)
            movinghead_pan_imag = np.rad2deg(np.arccos(vector_xy_plane[0]/vector_xy_plane_sum)) + int(shows_data["panrot"])
            if direction_vector_lamp_point[1] < 0: movinghead_pan_imag = 360 - movinghead_pan_imag + int(shows_data["panrot"])

            if movinghead_tilt_imag <= -45: movinghead_tilt_imag = -45
            if movinghead_tilt_imag >= 225: movinghead_tilt_imag = 225
            if movinghead_pan_imag <= 0: movinghead_pan_imag = 0
            if movinghead_pan_imag >= 520 : movinghead_pan_imag = 520

            movinghead_tilt = movinghead_tilt_imag + 45
            movinghead_pan = movinghead_pan_imag
            camera_pan = self.camera_pan_imag
            camera_tilt = self.camera_tilt_imag + 50

            camera_dmx = self.degrees_to_dmx(camera_pan, camera_tilt, 530, 280)
            movinghead_dmx = self.degrees_to_dmx(movinghead_pan, movinghead_tilt, 540, 270)

            self.universe[int(shows_data["mh_addr"])-1:(int(shows_data["mh_addr"])) + 4-1] = movinghead_dmx[0:4]
            self.universe[int(shows_data["cam_addr"])-1:(int(shows_data["cam_addr"])) + 4-1] = [camera_dmx[0],camera_dmx[2],camera_dmx[1],camera_dmx[3]]

            self.universe[(int(shows_data["mh_addr"])) + 39-1-1] = self.percent_to_dmx(int(parsed_data["dim"]))
            self.universe[(int(shows_data["mh_addr"])) + 12-1-1] = self.percent_to_dmx(int(parsed_data["dim"]))
            self.universe[(int(shows_data["mh_addr"])) + 32-1-1] = self.percent_to_dmx(int(parsed_data["zoom"]))
            self.universe[(int(shows_data["mh_addr"])) + 34-1-1] = self.percent_to_dmx(int(parsed_data["focus"]))
            if int(parsed_data["dim"]) != 0: self.universe[int(shows_data["mh_addr"])+38-1-1] = 34

            return self.universe, distance, int(x), int(y), int(z), int(movinghead_pan_imag), int(movinghead_tilt_imag), int(self.camera_pan_imag), int(self.camera_tilt_imag)

        except Exception as e:
            error = str(e)
            return [], error, error, error, error, error, error, error, error
    
    def degrees_to_dmx(self, pan:float, tilt:float, max_pan:int, max_tilt:int) -> list:
        """
        Converts degrees to DMX values for pan and tilt angles.
        
        Args:
            pan (float): The pan angle.
            tilt (float): The tilt angle.
            max_pan (int): The maximum pan angle.
            max_tilt (int): The maximum tilt angle.
        
        Returns:
            list: A list containing the DMX values for pan and tilt.
        """
        pan_ges = (pan*255/max_pan)
        pan_dmx = int(round(pan_ges - (pan_ges % 1), 0))
        pan_fine_dmx = int(round((pan_ges % 1)/0.5 * 127, 0))
        tilt_ges = (tilt*255/max_tilt)
        tilt_dmx = int(round(tilt_ges - (tilt_ges % 1), 0))
        tilt_fine_dmx = int(round((tilt_ges % 1)/0.5 * 127, 0))

        return [abs(pan_dmx), abs(pan_fine_dmx), abs(tilt_dmx), abs(tilt_fine_dmx)]
    
    def percent_to_dmx(self, value:int) -> int:
        """
        Converts a percentage value to DMX.
        
        Args:
            value (int): The percentage value.
        
        Returns:
            int: The corresponding DMX value.
        """
        return int((255/100)*value)
