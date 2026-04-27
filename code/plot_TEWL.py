import data_read
import glob
import os
import all_subjects_data_collector
import plotting

if __name__ == "__main__":

    plot_dir = "../data_out/tewl/"
    os.makedirs(plot_dir, exist_ok=True)

    # Data input location
    vivosight_folder = "data/Vivosight_data/"
    scan_folder = "data/scan_information/"
    tewl_folder = "data/TEWL_Data/"
    file_subject_codes = "data/SubjectCodes.xlsx"

    ### Get a list of all files
    files_tewl_raw = glob.glob("data/TEWL_Data/*.xls")

    # Read new codes
    file_subject_codes = "data/SubjectCodes.xlsx"
    subject_codes = data_read.read_subject_codes_and_doses(file_subject_codes)

    # Subje ct id modifications
    subject_id_skip = ["E50", "Leena", "R22", "E11"]
    subject_id_swap = {"Z47": "Z65"}

    # Collect depth data for plotting, boxplot data, and scatter data
    collector = all_subjects_data_collector.AllSubjectsDataCollector(
        vivosight_folder=vivosight_folder,
        scan_folder=scan_folder,
        tewl_folder=tewl_folder,
        subject_codes_file=file_subject_codes,
        subject_id_skip=subject_id_skip,
    )

    collector.get_subject_ids()
    collector.get_subject_codes(subject_id_swap)
    subject_data = collector.get_tewl_data()

    for _, subject in subject_data.items():
        subject.plot_tewl_data(plot_dir)

    plotting.plot_tewl_subject_averages_by_location(
        subject_data,
        plot_dir + "tewl_average_by_location_all_subjects.pdf",
    )
