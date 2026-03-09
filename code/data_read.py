from typing import Literal
import pandas as pd
import glob
from pathlib import Path
import re
import data_types
import numpy as np
import Epidermal as epi
import Bloodflow as bflow
import SkinRoughness as skin
import SkinSurface as skins


def collect_subject_vivosight_folder(
    subject: str, vivosight_path: str, scan_path: str, merge_return: bool
):

    directory = Path(vivosight_path)
    matching_folders = []

    for folder in directory.iterdir():
        if folder.is_dir():
            folder_name = folder.name
            base_id = folder_name.split("_")[0]
            is_return = "_2" in folder_name

            # Exact match considering return visits
            folder_full_id = base_id + ("_2" if is_return else "")

            if merge_return:
                # Merge return visits: A52 matches both A52 and A52_2
                if base_id == subject:
                    matching_folders.append(vivosight_path + folder_name)
            else:
                # Don't merge: A52 only matches A52, A52_2 only matches A52_2
                if folder_full_id == subject:
                    matching_folders.append(vivosight_path + folder_name)

    scan_folders = collect_subject_scan_folder(subject, scan_path, merge_return)

    return matching_folders, scan_folders


def collect_subject_scan_folder(subject: str, scan_path: str, merge_return: bool):

    matching_folders = []
    files = glob.glob(scan_path + "/*")

    for file in files:
        folder_name = file.split("/")[-1]

        # Extract base ID - look for letter followed by digits (e.g., D47, A52)
        match = re.search(r"([A-Z]\d+)", folder_name)
        if not match:
            continue

        base_id = match.group(1)
        is_return = "_2" in folder_name

        # Exact match considering return visits
        folder_full_id = base_id + ("_2" if is_return else "")

        if merge_return:
            # Merge return visits: A52 matches both A52 and A52_2
            if base_id == subject:
                matching_folders.append(file)
        else:
            # Don't merge: A52 only matches A52, A52_2 only matches A52_2
            if folder_full_id == subject:
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
    data_type: Literal["epidermal", "bloodflow", "skin roughness", "skin surface"],
    merge_return=False,
    exposure=None,
):
    """
    Process subject data for a specific data type (epidermal, bloodflow, or skin roughness).

    Args:
        data_type (str): The type of data to process ('epidermal', 'bloodflow', 'skin roughness').
        folder (str): The folder containing the subject data.
        subject_id (str, optional): The subject ID to process. If None, it will be inferred from the folder.
        merge_return (bool): If return, subject IDs are merged for return visits.

    Returns:
        dict: A dictionary containing the processed subject data.
    """

    _vivo_folders, _scan_folders = collect_subject_vivosight_folder(
        subject_id, vivo_path, scan_path, merge_return
    )

    # Check if return visit aka list of length 2
    # and subject_id contains '_2'
    if len(_vivo_folders) > 1:
        vivo_folders = sorted(_vivo_folders, key=lambda x: "_2" in x)
        scan_folders = sorted(_scan_folders, key=lambda x: "_2" in x)
    else:
        vivo_folders = _vivo_folders
        scan_folders = _scan_folders

    # subject_id = collect_subject_id_from_folder(vivo_folders[0])
    subject = data_types.Subject(subject_id=subject_id, exposure=exposure)

    for vivo_file, scan_file in zip(vivo_folders, scan_folders):
        data_folder = find_matching_subfolder(vivo_file, data_type)

        return_visit = collect_subject_id_return_from_folder(vivo_file)

        visit_data = data_types.Visit(subject)

        visit_data.process_subject_scan_data(scan_file, return_visit=return_visit)

        assert all(visit_data.before_locations == visit_data.after_locations)

        data_files = glob.glob(str(data_folder) + "/*.csv")

        # Fix for surface area files
        if len(data_files) == 0:
            data_files = [
                f for f in glob.glob(str(data_folder) + "/*") if not f.endswith(".xlsx")
            ]

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
                print(
                    f"Scan ID: {scan_id} not found for {subject_id} and file {data_file}"
                )
                exposed = True

            # Determine location of 1,2,3,4
            # Note: going from shoulder to wrist the orientation is [3,1,2,4]
            min_location_id = np.max(visit_data.before_locations) - 4
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
                        epi.Epidermal(
                            data_file,
                            scan_id,
                            exposed,
                            location_id,
                            exposure,
                            return_visit,
                        )
                    )
                elif data_type.lower() == "bloodflow":
                    visit_data.add_blood_flow(
                        bflow.BloodFlow(
                            data_file, scan_id, exposed, location_id, return_visit
                        )
                    )
                elif data_type.lower() == "skin roughness":
                    visit_data.add_skin_roughness(
                        skin.SkinRoughness(
                            data_file, scan_id, exposed, location_id, return_visit
                        )
                    )
                elif data_type.lower() == "surface area":
                    visit_data.add_skin_surface(
                        skins.SkinSurface(
                            data_file, scan_id, exposed, location_id, return_visit
                        )
                    )

            except Exception as e:
                print(f"Error reading {data_file}: {e}")

        if merge_return and return_visit:
            subject.return_visit = visit_data
        else:
            subject.visit = visit_data

    return subject


def get_all_subject_ids(vivosight_folder: str, return_visit: bool = False):
    """
    From the viosight folder retun a list of all unique subject ids

    If return_visit is True, do not combine IDs when "_2" in folder.

    """
    import glob

    folder = glob.glob(vivosight_folder + "/*")
    subject_ids = []
    for fold in folder:
        _id = fold.split("/")[-1].split("_")[0]
        if fold.split("/")[-1].split("_")[1] == "2" and return_visit:
            _id = _id + "_2"
        if _id not in subject_ids:
            subject_ids.append(_id)

    return subject_ids


def read_subject_codes_and_doses(input_file: str):
    """
    Read the xlsx file that contains the columns:
        PID | NEW PID | Exposure Group

    Args:
        input_file (str): Path to the Excel (.xlsx) file.

    Returns:
        subjects (dict): Mapping
            {
                PID: {
                    "new_pid": str,
                    "exposure": str
                }
            }
    """
    df = pd.read_excel(input_file)

    expected_cols = {"PID", "NEW PID", "Exposure Group"}
    if not expected_cols.issubset(df.columns):
        missing = expected_cols - set(df.columns)
        raise ValueError(f"Missing required columns: {missing}")

    subjects = {}

    for _, row in df.iterrows():
        pid = str(row["PID"]).strip()
        subjects[pid] = {
            "new_pid": str(row["NEW PID"]).strip(),
            "exposure": str(row["Exposure Group"]).strip(),
        }

    return subjects
