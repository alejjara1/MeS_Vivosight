from dataclasses import dataclass, field
from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


@dataclass
class Bloodscan:
    max_density: float
    depth_max_diameter: float
    max_diameter: float
    plexus_depth: float


@dataclass
class LocationData:
    pre: List[Bloodscan] = field(default_factory=list)
    post: List[Bloodscan] = field(default_factory=list)

    def add_pre(
        self,
        max_density: float,
        depth_max_diameter: float,
        max_diameter: float,
        plexus_depth: float,
    ):
        self.pre.append(
            Bloodscan(max_density, depth_max_diameter, max_diameter, plexus_depth)
        )

    def add_post(
        self,
        max_density: float,
        depth_max_diameter: float,
        max_diameter: float,
        plexus_depth: float,
    ):
        self.post.append(
            Bloodscan(max_density, depth_max_diameter, max_diameter, plexus_depth)
        )

    # def get_pre_average(self):
    #     values = [
    #         p.max_diameter
    #         for p in self.pre
    #         if p.max_diameter is not None and p.max_diameter > 0
    #     ]
    #     return np.mean(values) if len(values) > 1 else None

    # def get_post_average(self):
    #     values = [
    #         p.max_diameter
    #         for p in self.post
    #         if p.max_diameter is not None and p.max_diameter > 0
    #     ]
    #     return np.mean(values) if len(values) > 1 else None


class BloodFlow:
    def __init__(self, data_file, scan_id, exposed, location, return_visit):
        self.data_file = data_file
        bloodflow_depth_data = pd.read_csv(data_file, header=1, encoding="latin1")
        self.depth = bloodflow_depth_data["Depth (mm)"]
        self.vascular_density = bloodflow_depth_data["Vascular density"]
        self.vessel_diameter = bloodflow_depth_data["Vessel diameter"]
        plexus_data = pd.read_csv(data_file, header=0, nrows=0, encoding="latin1")
        self.plexus_depth = float(plexus_data.columns[1].split(" ")[0])
        self.scan_id = scan_id
        self.exposed = exposed
        self.location = location
        self.return_visit = return_visit
        self.max_density = None
        self.max_diameter = None

    def plot_vascular_density(self, subject_id):
        """
        Plot the vasuclar density plot ( vessel depth and vessel density)
        """
        fig, ax = plt.subplots()
        plt.plot(
            self.depth,
            self.vascular_density,
        )

        # plt.xticks(visible=False)
        if self.exposed:
            plt.title(
                f"Subject id: {subject_id}  Scan id: {self.scan_id} Post-Exposure Location {self.location}"
            )
        else:
            plt.title(
                f"Subject id: {subject_id}  Scan id: {self.scan_id} Pre-Exposure Location {self.location}"
            )
        plt.ylim(bottom=0)
        plt.ylabel("")
        plt.xlabel("Depth (mm)")
        plt.xlim(bottom=0)
        plt.legend()
        # plt.savefig(f"../data_out/epidermal_data_out/subject_id_{subject_id}_scan_id_{self.scan_id}.pdf")
        # plt.close()
        plt.show()

    def get_max_density(self):
        """Find the maximum density value and covert to percent"""
        self.max_density = self.vascular_density.max() * 100
        return self.max_density

    def get_max_diameter(self):
        """ "Find the maximum diameter value."""
        self.max_diameter = self.vessel_diameter.max()
        return self.max_diameter

    def get_depth_max_diameter(self):
        """Find the location at the maximum diameter value."""
        index = np.argmax(self.vessel_diameter)
        return self.depth[index]

    def set_blood_scan_data(self, blood_data):
        """
        Sets the blood scan data
        """
        if self.exposed:
            blood_data[self.location].add_post(
                self.get_max_density(),
                self.get_depth_max_diameter(),
                self.get_max_diameter(),
                self.plexus_depth,
            )
        else:
            blood_data[self.location].add_pre(
                self.get_max_density(),
                self.get_depth_max_diameter(),
                self.get_max_diameter(),
                self.plexus_depth,
            )

        return blood_data
