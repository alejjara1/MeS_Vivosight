from typing import Literal
import pandas as pd
import glob
from pathlib import Path
import numpy as np
import data_types
import re

#testing 
def collect_subject_vivosight_folder(subject: str, vivosight_path: str, scan_path: str):

    directory = Path(vivosight_path)
    matching_folders = [
        vivosight_path + folder.name
        for folder in directory.iterdir()
        if folder.is_dir() and folder.name.startswith(subject)
    ]

    scan_folders = collect_subject_scan_folder(subject, scan_path)

    return matching_folders, scan_folders


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


def collect_subject_id_return_from_folder(folder_in: str) -> bool:
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

    match = re.search(r"_L(\d+)", file_in)
    if match:
        location_id = match.group(1)
    else:
        raise ValueError

    return int(location_id)


def process_subject_vivosight_data(
    subject_id,
    vivo_path,
    scan_path,
    data_type: Literal["epidermal", "bloodflow", "skin roughness"],
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

    _vivo_folders, _scan_folders = collect_subject_vivosight_folder(
        subject_id,
        vivo_path,
        scan_path,
    )

    # Check if return visit aka list of length 2
    # and subject_id contains '_2'
    if len(_vivo_folders) > 1:
        vivo_folders = sorted(_vivo_folders, key=lambda x: "_2" in x)
        scan_folders = sorted(_scan_folders, key=lambda x: "_2" in x)
    else:
        vivo_folders = _vivo_folders
        scan_folders = _scan_folders

    subject_id = collect_subject_id_from_folder(vivo_folders[0])
    subject = data_types.Subject(subject_id=subject_id)

    for vivo_file, scan_file in zip(vivo_folders, scan_folders):
        data_folder = find_matching_subfolder(vivo_file, data_type)

        return_visit = collect_subject_id_return_from_folder(vivo_file)

        visit_data = data_types.Visit()

        visit_data.process_subject_scan_data(scan_file, return_visit=return_visit)

        data_files = glob.glob(str(data_folder) + "/*.csv")

        for data_file in data_files:
            location = collect_data_location(data_file)
            _location_id = collect_location_id(data_file)
            scan_id = collect_scan_id(data_file)
            arm = collect_arm_id_from_file(data_file)

            # Determine if pre or post exposure
            if scan_id in visit_data.before_scan_id.values:
                exposed = False
            elif scan_id in visit_data.after_scan_id.values:
                exposed = True
            else:
                exposed = None

            # Determine location of 1,2,3,4
            # Note: going from shoulder to wrist the orientation is [3,1,2,4]
            min_location_id = np.max(visit_data.locations) - 4
            location_id = int(_location_id - min_location_id)

            if subject_id == "M16":
                if _location_id == 1266:
                    location_id = 1
                elif _location_id == 1267:      
                    location_id = 2         
                elif _location_id == 1269:
                    location_id = 3
                elif _location_id == 1270:          
                    location_id = 4

            if subject_id == "Z47":
                if _location_id == 1244:
                    location_id = 1
                elif _location_id == 1246:      
                    location_id = 2         
                elif _location_id == 1247:
                    location_id = 3
                elif _location_id == 1248:          
                    location_id = 4


            try:
                if data_type == "epidermal":
                    visit_data.add_epidermal(
                        data_types.Epidermal(
                            data_file, scan_id, exposed, location_id, return_visit
                        )
                    )
                elif data_type.lower() == "bloodflow":
                    visit_data.add_blood_flow(
                        data_types.BloodFlow(
                            data_file, scan_id, exposed, location_id, return_visit
                        )
                    )
                elif data_type.lower() == "skin roughness":
                    visit_data.add_skin_roughness(
                        data_types.SkinRoughness(
                            data_file, scan_id, exposed, location_id, return_visit
                        )
                    )
            except Exception as e:
                print(f"Error reading {data_file}: {e}")

        print(vivo_file, visit_data.blood_flow)

        if return_visit:
            subject.return_visit = visit_data
        else:
            subject.visit = visit_data

    return subject


def get_all_subject_ids(vivosight_folder: str):
    """
    From the viosight folder retun a list of all unique subject ids
    """
    import glob

    folder = glob.glob(vivosight_folder + "/*")
    subject_ids = []
    for fold in folder:
        _id = fold.split("/")[-1].split("_")[0]
        if _id not in subject_ids:
            subject_ids.append(_id)

    return subject_ids
