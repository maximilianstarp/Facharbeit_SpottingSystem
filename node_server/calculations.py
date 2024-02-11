# import libraries
import json
import numpy as np
import pandas as pd
import requests
from functools import lru_cache

@lru_cache
class DMXCalculator():
    def __init__(self) -> None:
        self.camera_pan = 0
        self.camera_tilt = 0
        self.universe = [0]*512
    
    def get_distance(self, camera_ip:str, camera_port:int) -> str:
        try:
            distance = requests.get(f"http://{camera_ip}:{camera_port}", timeout=0.03)
            return distance.text
        except:
            return None
    
    def calculate_dmx_universe(self, values, shows_data):
        distance = self.get_distance(camera_ip=shows_data["ip_cam"], camera_port=shows_data["port_cam"])
        parsed_data = json.loads(pd.DataFrame({"values": values})["values"].iloc[0])

        try:
            distance = 5
            if distance == None: return[], "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found", "Cam not found"

            vector_lamp = [shows_data["xdist"], shows_data["ydist"], shows_data["zdist"]]

            self.camera_pan += float(parsed_data["Axis 0"]) * float(parsed_data["speed"]) * (-1)
            self.camera_tilt += float(parsed_data["Axis 1"]) * float(parsed_data["speed"]) * (-1)

            x = distance * np.cos(np.deg2rad(self.camera_tilt)) * np.cos(np.deg2rad(self.camera_pan))
            y = distance * np.cos(np.deg2rad(self.camera_tilt)) * np.sin(np.deg2rad(self.camera_pan))
            z = distance * np.sin(np.deg2rad(self.camera_tilt))


            direction_vector = [vector_lamp[0] - x, vector_lamp[1] - y, vector_lamp[2] - z]

            if (vector_lamp[0] - x) != 0.0: movinghead_pan =  np.arctan((vector_lamp[1] - y) / (vector_lamp[0] - x))
            else: movinghead_pan =  np.arctan(vector_lamp[1] - y / 0.001)
            if np.sqrt(direction_vector[0] ** 2 + direction_vector[1] ** 2 + direction_vector[2] ** 2) != 0: movinghead_tilt = np.arcsin((vector_lamp[2] - z) / (np.sqrt(direction_vector[0] ** 2 + direction_vector[1] ** 2 + direction_vector[2] ** 2)))
            else: movinghead_tilt = np.arcsin((vector_lamp[2] - z) / 0.001)

            movinghead_pan = np.rad2deg(movinghead_pan)
            movinghead_tilt = np.rad2deg(movinghead_tilt)


            self.universe[int(shows_data["mh_addr"]-1):(int(shows_data["mh_addr"]) + 5-1)] = self.degrees_to_dmx(movinghead_pan, movinghead_tilt, 540, 270)
            self.universe[int(shows_data["cam_addr"]-1):(int(shows_data["cam_addr"]) + 3-1)] = self.degrees_to_dmx(self.camera_pan, self.camera_tilt, 540, 270)
            self.universe[(int(shows_data["mh_addr"]) + 39-1)] = self.percent_to_dmx(int(parsed_data["dim"]))
            self.universe[(int(shows_data["mh_addr"]) + 12-1)] = self.percent_to_dmx(int(parsed_data["dim"]))
            self.universe[(int(shows_data["mh_addr"]) + 32-1)] = self.percent_to_dmx(int(parsed_data["zoom"]))
            self.universe[(int(shows_data["mh_addr"]) + 34-1)] = self.percent_to_dmx(int(parsed_data["focus"]))

            if int(parsed_data["dim"]) != 0: self.universe[int(shows_data["mh_addr"])+38] = 34

            return self.universe, distance, x, y, z, movinghead_pan, movinghead_tilt, self.camera_pan, self.camera_tilt

        except Exception as e:
            error = str(e)
            return [], error, error, error, error, error, error, error, error
    
    def degrees_to_dmx(self, pan:float, tilt:float, max_pan:int, max_tilt:int) -> list:
        pan_ges = (pan*255/max_pan)
        pan_dmx = int(round(pan_ges - (pan_ges % 1), 0))
        pan_fine_dmx = int(round((pan_ges % 1)/0.5 * 127, 0))
        tilt_ges = (tilt*255/max_tilt)
        tilt_dmx = int(round(tilt_ges - (tilt_ges % 1), 0))
        tilt_fine_dmx = int(round((tilt_ges % 1)/0.5 * 127, 0))

        return [abs(pan_dmx), abs(pan_fine_dmx), abs(tilt_dmx), abs(tilt_fine_dmx)]
    
    def percent_to_dmx(self, value:int) -> int:
        return int((255/100)*value)