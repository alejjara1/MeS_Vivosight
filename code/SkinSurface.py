from dataclasses import dataclass, field
from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


@dataclass
class SkinSurfacescan:
    surface_area: float


@dataclass
class LocationData:
    pre: List[SkinSurfacescan] = field(default_factory=list)
    post: List[SkinSurfacescan] = field(default_factory=list)

    def add_pre(
        self,
        surface_area: float,
    ):
        self.pre.append(SkinSurfacescan(surface_area))

    def add_post(
        self,
        surface_area: float,
    ):
        self.post.append(SkinSurfacescan(surface_area))


class SkinSurface:
    def __init__(self, data_file, scan_id, exposed, location, return_visit):
        self.data_file = data_file
        self.surface_area = self.extract_surface_area()
        self.scan_id = scan_id
        self.exposed = exposed
        self.location = location
        self.return_visit = return_visit

    def extract_surface_area(self):
        with open(self.data_file, "r") as f:
            for line in f:
                if "Selection Surface Area is" in line:
                    # Split and take the last value
                    return float(line.strip().split()[-1])

    def get_skin_surface_data(self, skin_surface_data):
        """
        Get the skin roughness data
        """
        if self.exposed:
            skin_surface_data[self.location].add_post(
                self.surface_area,
            )
        else:
            skin_surface_data[self.location].add_pre(
                self.surface_area,
            )

        return skin_surface_data
