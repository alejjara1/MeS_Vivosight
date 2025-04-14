from typing import Literal
import pandas as pd
import glob
from pathlib import Path
import numpy as np
import data_types


def collect_subject_vivosight_folder(subject: str, vivosight_path: str, scan_path: str):

    directory = Path(vivosight_path)
    matching_folders = [
        vivosight_path + folder.name
        for folder in directory.iterdir()
        if folder.is_dir() and folder.name.startswith(subject)
    ]

    print(subject,scan_folder)
    scan_folder = collect_subject_scan_folder(subject, scan_path)

    return matching_folders,scan_folder


def collect_subject_scan_folder(subject: str, scan_path: str):

    matching_folders = []
    files = glob.glob(scan_path + "/*")
    for file in files:
        if subject in file:
            matching_folders.append(file)

    return matching_folders


def find_matching_subfolder(path: str, target: str) -> Path | None:
    parent = Path(path)
    target = target.lower().replace(" ", "")
    for subfolder in parent.iterdir():
        if subfolder.is_dir():
            name = subfolder.name.lower().replace(" ", "")
            if target in name:
                return subfolder
    return None


def collect_subject_id_from_folder(folder_in: str) -> str:
    """
    Determine the subject id from the input TEWL file name which has the format:

    """
    subject_id = folder_in.split("/")[-1].split("_")[0]
    return subject_id


def collect_subject_id_return_from_folder(folder_in: str) -> str:
    """
    Determine the subject id from the input TEWL file name which has the format:

    """
    subject_id = folder_in.split("/")[-1].split("_")[1]
    if subject_id == "2":
        return True
    else:
        return False


def collect_subject_id_scan_information(file_in: str) -> str:
    """
    Determine the subject id from the input TEWL file name which has the format:

    """
    subject_id = file_in.split("/")[-1].split("_")[2]
    return subject_id


def collect_data_location(file_in: str) -> str:
    """
    Determine the subject id from the input TEWL file name which has the format:
    """
    location = file_in.split("/")[-1].split("_")[2]
    return location



def collect_scan_id(file_in: str) -> int:
    """
    Determine the subject id from the input TEWL file name which has the format:
    """
    scan_id = file_in.split("/")[-1].split("_")[3]
    if "L" in scan_id:
        scan_id = file_in.split("/")[-1].split("_")[4]
    return int(scan_id[1:])


def collect_arm_id_from_file(file_in: str) -> int:
    """ """
    arm_id = file_in.split("/")[-1].split(".")[0].split("_")[1].split(" ")[0]

    return arm_id

def collect_location_id(file_in: str) -> int:
    """
    Collect the location id from file names. LXXXX
    """
    location_id =  file_in.split("/")[-1].split(".")[0].split("Forearm")[1].split("_")[1][1:]
    return int(location_id)

def process_subject_vivosight_data(
    vivo_folder, scan_folder,  data_type: Literal["epidermal", "bloodflow", "skin roughness"]
):
    """
    Process subject data for a specific data type (epidermal, bloodflow, or skin roughness).

    Args:
        data_type (str): The type of data to process ('epidermal', 'bloodflow', 'skin roughness').
        folder (str): The folder containing the subject data.
        subject_id (str, optional): The subject ID to process. If None, it will be inferred from the folder.

    Returns:
        dict: A dictionary containing the processed subject data.
    """

    subject_id = collect_subject_id_from_folder(vivo_folder)
    return_visit = collect_subject_id_return_from_folder(vivo_folder)
    subject_data = data_types.Subject(subject_id=subject_id)

    subject_data = process_subject_scan_data(scan_folder,subject_data)

    data_folder = find_matching_subfolder(vivo_folder, data_type)

    data_files = glob.glob(str(data_folder) + "/*.csv")

    for data_file in data_files:
        location = collect_data_location(data_file)
        _location_id = collect_location_id(data_file)
        scan_id = collect_scan_id(data_file)
        arm = collect_arm_id_from_file(data_file)

        # Determine if pre or post exposure
        if scan_id in subject_data.before_scan_id.values:
            exposed = False
        elif scan_id in subject_data.after_scan_id.values:
            exposed = True
        else:
            exposed = None

        # Determine location of 1,2,3,4
        # Note: going from shoulder to wrist the orientation is [3,1,2,4]
        min_location_id = np.max(subject_data.locations) - 4
        location_id = int(_location_id - min_location_id)

        try:
            if data_type == "epidermal":
                subject_data.add_epidermal(
                    data_types.Epidermal(data_file, scan_id, exposed, location_id, return_visit)
                )
            elif data_type.lower() == "bloodflow":
                subject_data.add_blood_flow(
                    data_types.BloodFlow(data_file, scan_id, exposed, location_id, return_visit)
                )
            elif data_type.lower() == "skin roughness":
                subject_data.add_skin_roughness(
                    data_types.SkinRoughness(data_file, scan_id, exposed, location_id, return_visit)
                )
        except Exception as e:
            print(f"Error reading {data_file}: {e}")

    return subject_data


def process_subject_scan_data(file: str, subject_data = None):
    """ """

    subject_id = collect_subject_id_scan_information(file)
    try:
        data_before_exp = pd.read_excel(file, "Surface Area_BE")
        data_after_exp = pd.read_excel(file, "Surface Area_AE")
    except Exception as reason:
        data_before_exp = None
        data_after_exp = None
        print(
            f"There is an issue with \t {file}. \t This data will be excluded from the analysis. Reason: {reason}"
        )

    if subject_data is not None:
        subject_data.add_scan_data(data_before_exp,data_after_exp )
    else:
        subject_data = data_types.Subject(subject_id=subject_id)
        subject_data.add_scan_data(data_before_exp,data_after_exp )

    return subject_data


def get_all_subject_ids(vivosight_folder:str):
    """
    From the viosight folder retun a list of all unique subject ids
    """
    import glob
    folder = glob.glob(vivosight_folder+"/*")
    subject_ids = []
    for fold in folder:
        _id = fold.split("/")[-1].split("_Results")[0]
        subject_ids.append(_id)

    return subject_ids