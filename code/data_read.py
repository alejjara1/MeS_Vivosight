from typing import Literal
import pandas as pd
import glob
from pathlib import Path

import data_types


def collect_subject_vivosight_folder(subject: str, vivosight_path: str):

    directory = Path(vivosight_path)
    matching_folders = [
        vivosight_path + folder.name
        for folder in directory.iterdir()
        if folder.is_dir() and folder.name.startswith(subject)
    ]

    return matching_folders


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


def process_subject_vivosight_data(
    folder, data_type: Literal["epidermal", "bloodflow", "skin roughness"]
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

    subject_id = collect_subject_id_from_folder(folder)
    return_visit = collect_subject_id_return_from_folder(folder)
    subject_data = data_types.Subject(subject_id=subject_id)

    data_folder = find_matching_subfolder(folder, data_type)

    data_files = glob.glob(str(data_folder) + "/*.csv")
    for data_file in data_files:
        location = collect_data_location(data_file)
        scan_id = collect_scan_id(data_file)
        arm = collect_arm_id_from_file(data_file)
        try:
            if data_type == "epidermal":
                subject_data.add_epidermal(
                    data_types.Epidermal(data_file, scan_id, location, return_visit)
                )
            elif data_type.lower() == "bloodflow":
                subject_data.add_blood_flow(
                    data_types.BloodFlow(data_file, scan_id, location, return_visit)
                )
            elif data_type.lower() == "skin roughness":
                subject_data.add_skin_roughness(
                    data_types.SkinRoughness(data_file, scan_id, location, return_visit)
                )
        except Exception as e:
            print(f"Error reading {data_file}: {e}")

    return subject_data


def process_subject_scan_data(file: str):
    """ """

    subject_id = collect_subject_id_scan_information(file)
    try:
        data_before_exp = pd.read_excel(file, "Surface Area_AE")
        data_after_exp = pd.read_excel(file, "Surface Area_BE")
    except Exception as reason:
        data_before_exp = None
        data_after_exp = None
        print(
            f"There is an issue with \t {file}. \t This data will be excluded from the analysis. Reason: {reason}"
        )

    # print(data_before_exp)
    b_scan_id = data_before_exp["Scan#"].dropna()
    b_location = data_before_exp["Location"].dropna()

    a_scan_id = data_after_exp["Scan#"].dropna()
    a_location = data_after_exp["Location"].dropna()

    if subject_id in subject_info_data:
        subject_info_data[subject_id]["before_scan_id"].extend(list(b_scan_id))
        subject_info_data[subject_id]["before_location"].extend(list(b_location))
        subject_info_data[subject_id]["after_scan_id"].extend(list(a_scan_id))
        subject_info_data[subject_id]["after_location"].extend(list(a_location))
    else:
        subject_info_data[subject_id] = {
            "before_scan_id": list(b_scan_id),
            "before_location": list(b_location),
            "after_scan_id": list(a_scan_id),
            "after_location": list(a_location),
        }
