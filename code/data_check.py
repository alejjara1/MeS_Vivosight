import data_read
import pandas as pd
import glob
import numpy as np
import os


def check_data_with_new_codes():
    """
    Compare the old subject IDs to the new codes in "data/SubjectCodes.xlsx"
    """
    # File paths
    vivosight_folder = "data/Vivosight_data/"
    scan_folder = "data/scan_information/"
    file_subject_codes = "data/SubjectCodes.xlsx"

    # Check VivoSight Data
    subject_ids = data_read.get_all_subject_ids(vivosight_folder)
    subject_codes = data_read.read_subject_codes_and_doses(file_subject_codes)
    vivo_missing = []  # ["E50", "Z47"]
    for n, subject_id in enumerate(subject_ids):
        if subject_id not in subject_codes:
            vivo_missing.append(subject_id)
            # print(n, subject_id, subject_codes[subject_id])

    vivo_code_missing = []  # ['Z65']
    for n, subject_code in enumerate(subject_codes.keys()):
        clean_subject_code = subject_code.split("_", 1)[0]
        if clean_subject_code not in subject_ids:
            vivo_code_missing.append(clean_subject_code)

    print("Vivo not in Codes", vivo_missing)
    print("Codes not in Vivo", vivo_code_missing)

    # Check TEWL Data
    files_tewl_raw = glob.glob("data/TEWL_Data/*.xls")

    tewl_ids = []
    tewl_missing = []  # ['E50' 'Leena' 'R22']\
    for file in files_tewl_raw:

        split_file = file.split("/")[-1].split(".")[0].split("_")
        subject_id = split_file[0]

        if split_file[1] == "R":
            subject_id = subject_id + "_R"

        if subject_id not in tewl_ids:
            tewl_ids.append(subject_id)

        if subject_id not in subject_codes:
            tewl_missing.append(subject_id)

    tewl_code_missing = []
    for n, subject_code in enumerate(subject_codes.keys()):
        clean_subject_code = subject_code.split("_", 1)[0]
        if clean_subject_code not in tewl_ids:
            tewl_code_missing.append(clean_subject_code)

    print("TEWL not in Codes", np.unique(tewl_missing))
    print("Codes not in TEWL", tewl_code_missing)

    # Check Scan Data
    files_scan_raw = glob.glob("data/scan_information/*.xlsx")

    scan_ids = []
    scan_missing = []
    for file in files_scan_raw:
        subject_id = file.split("/")[-1].split(".")[0].split("_")[2]
        if subject_id not in scan_ids:
            scan_ids.append(subject_id)

        if subject_id not in subject_codes:
            scan_missing.append(subject_id)

    scan_code_missing = []
    for n, subject_code in enumerate(subject_codes.keys()):
        clean_subject_code = subject_code.split("_", 1)[0]
        if clean_subject_code not in scan_ids:
            scan_code_missing.append(clean_subject_code)

    print("Scan not in Codes", np.unique(scan_missing))
    print("Codes not in Scan", scan_code_missing)


def check_epidermal_data():
    """
    Ensure that the epidermal data is complete.
    The epidermal data uses a lookup excel sheet to match scan numbers.
    """

    # Vivosight and Epidermal Data
    vivosight_folder = "data/Vivosight_data/"
    scan_folder = "data/scan_information/"

    # New codes and dose info
    file_subject_codes = "data/SubjectCodes.xlsx"
    subject_codes = data_read.read_subject_codes_and_doses(file_subject_codes)
    subject_id_skip = ["E50", "Leena", "R22"]
    subject_id_swap = {"Z47": "Z65"}

    # subject_id = "A52"
    subject_ids = data_read.get_all_subject_ids(vivosight_folder)

    subject_ids_with_same_before_after_scan_ids = []
    for subject_id in subject_ids:

        subject_data = data_read.process_subject_vivosight_data(
            subject_id, None, vivosight_folder, scan_folder, "epidermal"
        )

        if not all(
            subject_data.visit.before_scan_id != subject_data.visit.after_scan_id
        ):
            subject_ids_with_same_before_after_scan_ids.append(subject_id)

    print(
        f"These subjects have same before and after scan ids: {subject_ids_with_same_before_after_scan_ids}"
    )


def check_vivosight_files(data_type):
    """
    Compare Vivosight data files against the scan information Excel sheet.

    data_type is "epidermal" or "flows",

    """
    # Read the Excel sheet
    file_subject_codes = "data/Raw_Data_All_Redo.xlsx"
    df = pd.read_excel(file_subject_codes)

    # Get expected files from Excel
    vivosight_folder = "data/Vivosight_data/"
    expected_files = {}

    for _, row in df.iterrows():
        pid = row["PID"]
        repeat = row["Repeat"]
        date = row["DATE"]
        scan_id = row["Scan#"]
        location = row["Location"]
        # Create a unique key for matching
        key = f"{pid}_L{location}_S{scan_id}"
        expected_files[key] = row.to_dict()

    # Get all actual files from subdirectories
    actual_files = {}
    for filepath in glob.glob(f"{vivosight_folder}**/*_{data_type}*", recursive=True):
        filename = os.path.basename(filepath)
        # Parse filename: E50_Right Forearm_L1192_S647_07_15_2024_epidermal
        # or: F12_Left Forearm_L1237_S924_09_04_2024_epidermal
        parts = filename.split("_")

        # First part is always PID
        pid = parts[0]

        # Find L and S numbers by looking for parts that start with L or S
        l_num = None
        s_num = None
        for part in parts:
            if part.startswith("L") and part[1:].isdigit():
                l_num = part[1:]
            elif part.startswith("S") and part[1:].isdigit():
                s_num = part[1:]

        if l_num and s_num:
            key = f"{pid}_L{l_num}_S{s_num}"
            actual_files[key] = filepath

    # Compare
    expected_keys = set(expected_files.keys())
    actual_keys = set(actual_files.keys())

    missing_files = expected_keys - actual_keys
    extra_files = actual_keys - expected_keys

    print(f"Total expected: {len(expected_keys)}")
    print(f"Total found: {len(actual_keys)}")
    print(f"\nMissing files ({len(missing_files)}):")
    for key in sorted(missing_files):
        row = expected_files[key]
        print(
            f"  {key} - PID: {row['PID']}, Date: {row['DATE']}, Location: {row['Location']}, Scan: {row['Scan#']}"
        )

    if extra_files:
        print(f"\nExtra files ({len(extra_files)}):")
        for key in sorted(extra_files):
            print(f"  {key} - {actual_files[key]}")

    if not missing_files and not extra_files:
        print("\nAll files present and accounted for!")


if __name__ == "__main__":
    # check_data_with_new_codes()
    # check_epidermal_data()
    check_vivosight_files("epidermal")
    # check_vivosight_files("flows")
    # check_vivosight_files("roughness")
