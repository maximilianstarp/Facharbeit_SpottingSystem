# import libraries
import json
import numpy as np
import pandas as pd
import requests
from functools import lru_cache

class DMXCalculator():
    def __init__(self) -> None:
        self.camera_pan = 0
        self.camera_tilt = 0
        self.universe = [0]*512
    
    def get_distance(camera_ip:str, camera_port:int) -> str:
        try:
            distance = requests.get(f"http://{camera_ip}:{camera_port}", timeout=0.03)
            return distance.text
        except:
            return None
    
    def calculate_dmx_universe(self, values, shows_data):
        distance = self.get_distance(camera_ip=shows_data["camera_ip"], camera_port=shows_data["camera_port"])
        parsed_data = json.loads(pd.DataFrame({"values": values})["values"].iloc[0])

        try:
            if distance == None: return[], "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found"

            vector_lamp = [shows_data["xdist"], shows_data["ydist"], shows_data["zdist"]]

            self.pan_cam += float(parsed_data["Axis 0"]) * float(parsed_data["speed"]) * (-1)
            self.tilt_cam += float(parsed_data["Axis 1"]) * float(parsed_data["speed"]) * (-1)

            x = distance * np.cos(np.deg2rad(self.camera_tilt)) * np.cos(np.deg2rad(self.camera_pan))
            y = distance * np.cos(np.deg2rad(self.camera_tilt)) * np.sin(np.deg2rad(self.camera_pan))
            z = distance * np.sin(np.deg2rad(self.camera_tilt))

            direction_vector = [vector_lamp[0] - x, vector_lamp[1] - y, vector_lamp[2] - z]

            movinghead_pan =  np.arctan(vector_lamp[1] - y / vector_lamp[0] - x)
            movinghead_tilt = np.arcsin((vector_lamp[2] - z) / np.sqrt(direction_vector[0] ** 2 + direction_vector[1] ** 2 + direction_vector[2] ** 2))

            movinghead_pan = np.rad2deg(movinghead_pan)
            movinghead_tilt = np.rad2deg(movinghead_tilt)

            return self.universe, distance, x, y, z, movinghead_pan, movinghead_tilt, self.camera_pan, self.camera_tilt

        except Exception as e:
            error = str(e)
            return [], error, error, error, error, error, error, error, error
    
    def degrees_to_dmx(value:int) -> list:
        pass
