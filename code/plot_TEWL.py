import data_read
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os


def collect_subject_id_from_file(file_in: str) -> str:
    """
    Determine the subject id from the input TEWL file name which has the format:

    """
    split_file = file_in.split("/")[-1].split(".")[0].split("_")
    subject_id = split_file[0]

    return subject_id


def collect_return_visit_from_file(file_in: str) -> bool:
    """
    Determine from the input TEWL file name if is a return visit. Input file format:

        data/{subject_id}_{return visit = R}_{scan_id}.xls
    """
    return "_R_" in file_in.split("/")[-1].split(".")[0]


def collect_scan_id_from_file(file_in: str) -> int:
    """
    Determine the scan id from the input TEWL file name which has the format:

        data/{subject_id}_{return visit = R}_{scan_id}.xls
    """
    scan_id = int(file_in.split("/")[-1].split(".")[0].split("_")[-1])

    return scan_id


def collect_arm_id_from_file(file_in: str) -> int:
    """ """
    arm_id = file_in.split("/")[-1].split(".")[0].split("_")[-3]

    return arm_id


def collect_location_id_from_file(file_in: str) -> int:
    """ """
    location_id = int(file_in.split("/")[-1].split(".")[0].split("_")[-2])

    return location_id


def collect_pre_post_from_file(file_in: str) -> int:
    """ """
    name_check = file_in.split("/")[-1].split(".")[0].split("_")[-4]
    if name_check == "Leena":
        post_exposure = True
    else:
        post_exposure = False

    return post_exposure


class Scan:
    def __init__(
        self, scan_id, return_visit, data, arm=None, location=None, post_exposure=None
    ):
        self.scan_id = scan_id
        self.return_visit = return_visit
        self.data = data
        self.arm = arm
        self.location = location
        self.post_exposure = post_exposure


class Subject:
    def __init__(self, subject_id):
        self.subject_id = subject_id
        self.scans = None
        self.num_scans = 0

    def add_scan(
        self, scan_id, return_visit, data, arm=None, location=None, post_exposure=None
    ):
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
                scan_id=scan_id,
                return_visit=return_visit,
                data=data,
                arm=arm,
                location=location,
                post_exposure=post_exposure,
            )
        )
        self.num_scans += 1

    def plot_tewl_data(self, plot_dir):
        """
        Plot the TEWL data
        """

        colors = ["#1f77b4", "#2ca02c", "#ff7f0e"]
        fig, ax = plt.subplots()

        sorted_scans = sorted(self.scans, key=lambda x: (x.return_visit, x.scan_id))
        for scan in sorted_scans:
            if scan.return_visit:
                label_text = f"Return Visit (Scan {scan.scan_id})"
                ax.plot(
                    scan.data["TM_TEWL"],
                    linestyle="dotted",
                    label=label_text,
                    c=colors[scan.scan_id - 1],
                )
            else:
                if self.subject_id == "Leena":
                    continue
                label_text = f"Initial Visit (Scan {scan.scan_id})"
                ax.plot(
                    scan.data["TM_TEWL"],
                    label=label_text,
                    c=colors[scan.scan_id - 1],
                )

        ax.set_title(f"ID: {self.subject_id.replace('_', '-')}", fontsize=16)
        ax.set_xlabel("Time (seconds)", fontsize=14)
        ax.set_ylabel("TEWL (g/m2/h)", fontsize=14)

        ax.tick_params(axis="both", labelsize=12)

        ax.set_ylim(0, 15)
        ax.set_xlim(10, 40)

        ax.legend()
        fig.tight_layout()
        fig.savefig(plot_dir + f"tewl_{self.subject_id}.pdf")
        plt.close(fig)


if __name__ == "__main__":

    plot_dir = "../data_out/tewl/"
    os.makedirs(plot_dir, exist_ok=True)

    ### Get a list of all files
    files_tewl_raw = glob.glob("data/TEWL_Data/*.xls")

    # Read new codes
    file_subject_codes = "data/SubjectCodes.xlsx"
    subject_codes = data_read.read_subject_codes_and_doses(file_subject_codes)

    ### Control the output
    logging = True

    ### Initialize the data
    subject_data = {}
    subject_ids = []

    subject_id_skip = ["E50", "Leena", "R22"]

    ### Iterate through all of the data
    for file in files_tewl_raw:
        subject_id = collect_subject_id_from_file(file)

        if subject_id in subject_id_skip:
            continue

        new_subject_id = subject_codes[subject_id]["new_pid"]

        new_subject_id = new_subject_id.split("_")[0]

        scan_id = collect_scan_id_from_file(file)
        return_visit = collect_return_visit_from_file(file)

        print(file, subject_id, new_subject_id, return_visit)

        # print(file, subject_id, scan_id, return_visit)
        try:
            data = pd.read_excel(file)
        except Exception as reason:
            data = None
            if logging:
                print(
                    f"There is an issue with \t {file}. \t This data will be excluded from the analysis. Reason: {reason}"
                )

            continue
        if subject_id not in subject_data:
            subject_data[subject_id] = Subject(subject_id=new_subject_id)

        subject_data[subject_id].add_scan(
            scan_id=scan_id,
            return_visit=return_visit,
            data=data,
        )

    for subject_id, subject in subject_data.items():
        subject.plot_tewl_data(plot_dir)
