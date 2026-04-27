import matplotlib.pyplot as plt
import numpy as np


def collect_subject_id_from_file(file_in: str) -> str:
    """
    Determine the subject id from the input TEWL file name which has the format:

    """
    split_file = file_in.split("/")[-1].split(".")[0].split("_")
    subject_id = split_file[0]
    if split_file[1] == "R":
        subject_id = subject_id + "_2"

    return subject_id


def collect_return_visit_from_file(file_in: str) -> bool:
    """
    Determine from the input TEWL file name if is a return visit. Input file format:

        data/{subject_id}_{return visit = R}_{location}.xls
    """
    return "_R_" in file_in.split("/")[-1].split(".")[0]


def collect_location_from_file(file_in: str) -> int:
    """
    Determine the scan id from the input TEWL file name which has the format:

        data/{subject_id}_{return visit = R}_{location}.xls
    """
    location = int(file_in.split("/")[-1].split(".")[0].split("_")[-1])

    return location


def collect_arm_id_from_file(file_in: str) -> int:
    """ """
    arm_id = file_in.split("/")[-1].split(".")[0].split("_")[-3]

    return arm_id


def collect_pre_post_from_file(file_in: str) -> int:
    """ """
    name_check = file_in.split("/")[-1].split(".")[0].split("_")[-4]
    if name_check == "Leena":
        post_exposure = True
    else:
        post_exposure = False

    return post_exposure


class Scan:
    def __init__(self, location, return_visit, data, arm=None, post_exposure=None):
        self.location = location
        self.return_visit = return_visit
        self.data = data
        self.arm = arm
        self.post_exposure = post_exposure


class Subject:
    def __init__(self, subject_id):
        self.subject_id = subject_id
        self.scans = None
        self.num_scans = 0
        self.averages = {}

    def add_scan(self, location, return_visit, data, arm=None, post_exposure=None):
        """_summary_

        Args:
            visit_id (_type_): _description_
            return_visit (_type_): _description_
            data (_type_): _description_
        """
        if self.scans is None:
            self.scans = []

        self.scans.append(
            Scan(
                location=location,
                return_visit=return_visit,
                data=data,
                arm=arm,
                post_exposure=post_exposure,
            )
        )
        self.num_scans += 1

    def set_averages(self):
        """Calculates the average TEWL value"""
        for scan in self.scans:
            self.averages[scan.location] = {
                "data": np.average(scan.data["TM_TEWL"]),
                "return_visit": scan.return_visit,
            }

    def get_average(self, location=1):
        """Collect the average TEWL value at location"""
        if location in self.averages.keys():
            return self.averages[location]["data"]
        else:
            return None

    def plot_tewl_data(self, plot_dir):
        """
        Plot the TEWL data
        """

        colors = ["#1f77b4", "#2ca02c", "#ff7f0e"]
        fig, ax = plt.subplots()

        sorted_scans = sorted(self.scans, key=lambda x: (x.return_visit, x.location))
        for scan in sorted_scans:
            if scan.return_visit:
                label_text = f"Return Visit (Location {scan.location})"
                ax.plot(
                    scan.data["TM_TEWL"],
                    linestyle="dotted",
                    label=label_text,
                    c=colors[scan.location - 1],
                )
            else:
                if self.subject_id == "Leena":
                    continue
                label_text = f"Initial Visit (Location {scan.location})"
                ax.plot(
                    scan.data["TM_TEWL"],
                    label=label_text,
                    c=colors[scan.location - 1],
                )

        ax.set_title(f"ID: {self.subject_id.replace('_', '-')}", fontsize=16)
        ax.set_xlabel("Time (seconds)", fontsize=14)
        ax.set_ylabel("TEWL (g/m$^2$-h)", fontsize=14)

        ax.tick_params(axis="both", labelsize=12)

        ax.set_ylim(0, 15)
        ax.set_xlim(10, 40)

        ax.legend()
        fig.tight_layout()
        fig.savefig(plot_dir + f"tewl_{self.subject_id}.pdf")
        plt.close(fig)
