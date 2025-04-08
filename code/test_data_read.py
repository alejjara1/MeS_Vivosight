import data_read


# Example for Vivosight and Epidermal Data
vivosight_location = "../data/Vivosight_data/"
subject = "A52"
subject_folder = data_read.collect_subject_vivosight_folder(subject, vivosight_location)
subject_data = data_read.process_subject_vivosight_data(subject_folder[0], "epidermal")


# Example for Scan data - Not implemented yet
# scan_location = "../data/scan_information/"
# subject = "A52"
# subject_folder = data_read.collect_subject_scan_folder(subject, scan_location)
# subject_data = data_read.process_subject_scan_data(subject_folder[0])
# print(subject_folder)
