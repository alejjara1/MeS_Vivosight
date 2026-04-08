from dataclasses import dataclass, field
from typing import List
import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import os


@dataclass
class EpidermalScan:
    depth: float
    approach: int
    scan_id: int
    sid: float
    AuC: float
    attenuation_coeff: float


@dataclass
class LocationData:
    pre: List[EpidermalScan] = field(default_factory=list)
    post: List[EpidermalScan] = field(default_factory=list)

    def add_pre(
        self,
        depth: float,
        approach: int,
        scan_id: int,
        sid: float,
        AuC: float,
        attenuation_coeff: float,
    ):
        self.pre.append(
            EpidermalScan(depth, approach, scan_id, sid, AuC, attenuation_coeff)
        )

    def add_post(
        self,
        depth: float,
        approach: int,
        scan_id: int,
        sid: float,
        AuC: float,
        attenuation_coeff: float,
    ):
        self.post.append(
            EpidermalScan(depth, approach, scan_id, sid, AuC, attenuation_coeff)
        )

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


class Epidermal:
    def __init__(self, data_file, scan_id, exposed, location, exposure, return_visit):
        self.data_file = data_file
        self.depth_data = pd.read_csv(data_file, header=6, encoding="latin1")
        self.summary_data = pd.read_csv(
            data_file, header=None, nrows=6, encoding="latin1"
        )
        self.scan_id = scan_id
        self.exposed = exposed
        self.location = location
        self.exposure = exposure
        self.return_visit = return_visit
        self.min_value = None
        self.max_value = None
        self.min_location_index = None
        self.depth = None
        self.sid = None
        self.AuC = None
        self.attenuation_coeff = None

    def parse_summary_data(self):
        """
        Parse the summary statistics provided by Vivosight into a dict.
        """
        summary = {}
        for _, row in self.summary_data.iterrows():
            key = str(row.iloc[0]).strip()
            value = row.iloc[1]
            summary[key] = value

        return summary

    def find_min_max(self):
        """
        Find the minimum and maximum of the Mean A-scan data
        """
        self.min_value = self.depth_data["Mean A-scan"].min()
        self.max_value = self.depth_data["Mean A-scan"].max()

    def get_normalize_a_scan(self):
        """
        Normalize the Mean A-scan
        """
        self.find_min_max()
        self.depth_at_max_intensity = self.depth_data["Depth"][
            self.depth_data["Mean A-scan"].idxmax()
        ]
        self.normalized_a_scan = (self.depth_data["Mean A-scan"] - self.min_value) / (
            self.max_value - self.min_value
        )

    def get_sid(self):
        """
        Calculate the scaled intensity drop
        """
        value = 0.2
        index = abs(self.normalized_a_scan - value).idxmin()
        attenuation_depth = self.depth_data["Depth"].iloc[index]
        self.sid = 0.8 / attenuation_depth

    def get_AuC(self):
        """
        Integrate the curve
        """
        integration_depth = 0.2
        lower_bound_index = self.depth_data["Mean A-scan"].idxmax()

        upper_bound_index = abs(
            self.depth_data["Depth"] - (self.depth_at_max_intensity + integration_depth)
        ).idxmin()

        self.AuC = sp.integrate.trapezoid(
            self.normalized_a_scan[lower_bound_index:upper_bound_index],
            self.depth_data["Depth"][lower_bound_index:upper_bound_index],
        )

    def get_attenuation_coeff(self):
        """
        Grab the attenuation coefficient form the Epidermal scan data
        """
        summary = self.parse_summary_data()
        self.attenuation_coeff = float(summary["Attenuation coefficient / mm-1"])

    def get_epidermal_data(self, epidermal_data, approach=0):
        """
        Get the epidermal data
        """

        self.depth = self.get_inflection_depth(approach)
        self.get_normalize_a_scan()
        self.get_sid()
        self.get_AuC()
        self.get_attenuation_coeff()

        if self.exposed:
            epidermal_data[self.location].add_post(
                self.depth,
                approach,
                self.scan_id,
                self.sid,
                self.AuC,
                self.attenuation_coeff,
            )
        else:
            epidermal_data[self.location].add_pre(
                self.depth,
                approach,
                self.scan_id,
                self.sid,
                self.AuC,
                self.attenuation_coeff,
            )

        return epidermal_data

    def get_inflection_depth(self, approach=0):
        """
        Determines the inflection depth from a epidermal scan
        """

        if approach == 0:
            summary = self.parse_summary_data()
            depth = float(summary["Epidermal thickness / µm"]) / 1000  # unit conversion
        else:
            self.get_normalize_a_scan()
            if approach == 1:
                self.approach_1(15)
            elif approach == 2:
                self.approach_2(15, 200)

            depth = None
            if self.min_location_index is not None:
                depth = self.depth_data["Depth"][self.min_location_index]

        depth = depth * 1000  # unit conversion to um

        return depth

    def plot_a_scan(self, subject_id, derivative=False):
        """
        Plot the A-scan data
        """
        # Ensure the output directory exists
        output_dir = "../data_out/epidermal_data_out/" + subject_id
        os.makedirs(output_dir, exist_ok=True)

        fig, ax = plt.subplots()
        ax.plot(
            self.depth_data["Depth"],
            self.depth_data["Mean A-scan"],
            label="Mean A-Scan",
        )

        if derivative:
            smooth_deriv_vals, _ = self.compute_derivatives(smooth=True)
            ax2 = ax.twinx()
            ax2.plot(
                self.depth_data["Depth"],
                smooth_deriv_vals,
                color="orange",
                alpha=0.7,
                label="Derivative",
            )

            deriv_vals, _ = self.compute_derivatives()
            ax2.plot(
                self.depth_data["Depth"],
                deriv_vals,
                color="red",
                alpha=0.7,
                label="Derivative",
            )

            ax2.set_ylabel("Derivative", fontsize=14)
            ax2.tick_params(axis="y", labelsize=12)

        # Colors for different approaches
        approach_colors = {0: "black", 1: "green", 2: "red"}
        for approach in [0, 1, 2]:
            depth = self.get_inflection_depth(approach)
            if depth is None:
                continue
            # Find closest depth value without using index
            closest_idx = abs(self.depth_data["Depth"] - depth).idxmin()
            ax.plot(
                depth,
                self.depth_data["Mean A-scan"][closest_idx],
                "o",
                color=approach_colors[approach],
                fillstyle="none",
                label=f"Approach {approach}",
            )

        # Build title with all relevant information
        title_parts = [f"Subject ID: {subject_id}", f"Location {self.location}"]

        if self.exposed:
            title_parts.append(f"Scan {self.scan_id} (Post-Exposure)")
        else:
            title_parts.append(f"Scan {self.scan_id} (Pre-Exposure)")

        title_parts.append(f" - Approach {approach}")

        ax.set_title(" | ".join(title_parts))
        ax.set_ylim(bottom=0)
        ax.set_ylabel("Intensity", fontsize=14)
        ax.set_xlabel("Depth (mm)", fontsize=14)
        ax.tick_params(axis="both", labelsize=12)
        plt.xlim(0, 2)
        plt.legend()
        plt.savefig(f"{output_dir}/subject_id_{subject_id}_scan_id_{self.scan_id}.pdf")
        plt.close()

    def compute_derivatives(self, smooth=False):
        """Finding the first and second derivative."""
        n_points = len(self.normalized_a_scan)
        derivative = np.zeros_like(self.normalized_a_scan)
        second_derivative = np.zeros_like(self.normalized_a_scan)

        if smooth:
            f = sp.ndimage.gaussian_filter1d(self.normalized_a_scan, sigma=1.5)
        else:
            f = self.normalized_a_scan

        for n in range(1, n_points - 1):
            h = self.depth_data["Depth"][n] - self.depth_data["Depth"][n - 1]
            derivative[n] = (f[n + 1] - f[n - 1]) / (
                self.depth_data["Depth"][n + 1] - self.depth_data["Depth"][n - 1]
            )
            second_derivative[n] = (f[n + 1] - 2 * f[n] + f[n - 1]) / (h * h)

        return derivative, second_derivative

    def approach_1(self, begin_skip):
        """
        Function for approach 1 : derivative switches sign neg to pos
        """
        derivative, _ = self.compute_derivatives()
        old_value = derivative[begin_skip]
        for n in range(begin_skip + 1, 98):
            new_value = derivative[n]
            if old_value < 0 and new_value > 0:
                self.min_location_index = n
                break
            else:
                old_value = new_value

    def approach_2(self, begin_skip, end_skip):
        """location of the largest change in the derivative."""
        derivative, _ = self.compute_derivatives()
        diff = np.diff(derivative[begin_skip : len(self.normalized_a_scan) - end_skip])
        self.min_location_index = begin_skip + np.argmax(diff)
