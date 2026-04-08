from dataclasses import dataclass, field
from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


@dataclass
class Skinscan:
    Ra: float
    Rz: float
    Rq: float


@dataclass
class LocationData:
    pre: List[Skinscan] = field(default_factory=list)
    post: List[Skinscan] = field(default_factory=list)

    def add_pre(
        self,
        Ra: float,
        Rz: float,
        Rq: float,
    ):
        self.pre.append(Skinscan(Ra, Rz, Rq))

    def add_post(
        self,
        Ra: float,
        Rz: float,
        Rq: float,
    ):
        self.post.append(Skinscan(Ra, Rz, Rq))

    def get_pre_average(self, attribute: str):
        values = [
            getattr(p, attribute)
            for p in self.pre
            if getattr(p, attribute) is not None and getattr(p, attribute) > 0
        ]
        return np.mean(values) if len(values) > 1 else None

    def get_post_average(self, attribute: str):
        values = [
            getattr(p, attribute)
            for p in self.post
            if getattr(p, attribute) is not None and getattr(p, attribute) > 0
        ]
        return np.mean(values) if len(values) > 1 else None


class SkinRoughness:
    def __init__(self, data_file, scan_id, exposed, location, return_visit):
        self.data_file = data_file

        _roughness_data = pd.read_csv(data_file, header=None, encoding="latin1")
        self.Ra = _roughness_data.iloc[0, 1]
        self.Rz = _roughness_data.iloc[1, 1]
        self.Rq = _roughness_data.iloc[2, 1]
        self.scan_id = scan_id
        self.exposed = exposed
        self.location = location
        self.return_visit = return_visit

    def get_skin_roughness_data(self, skin_roughness_data):
        """
        Get the skin roughness data
        """
        if self.exposed:
            skin_roughness_data[self.location].add_post(
                self.Ra,
                self.Rz,
                self.Rq,
            )
        else:
            skin_roughness_data[self.location].add_pre(
                self.Ra,
                self.Rz,
                self.Rq,
            )

        return skin_roughness_data
