import os
import plotting
import outliers
import all_subjects_data_collector


if __name__ == "__main__":

    plot_dir = "../data_out/bloodflow/"
    os.makedirs(plot_dir, exist_ok=True)

    # Data input location
    vivosight_folder = "data/Vivosight_data/"
    scan_folder = "data/scan_information/"
    file_subject_codes = "data/SubjectCodes.xlsx"

    # Subject id modifications
    subject_id_skip = ["E50", "Leena", "R22"]
    subject_id_swap = {"Z47": "Z65"}

    collector = all_subjects_data_collector.AllSubjectsDataCollector(
        vivosight_folder=vivosight_folder,
        scan_folder=scan_folder,
        subject_codes_file=file_subject_codes,
        subject_id_skip=subject_id_skip,
    )

    collector.get_subject_ids()
    collector.get_subject_codes(subject_id_swap)
    subject_data = collector.get_bloodflow_data()

    data_types = ["max_density", "max_diameter", "plexus_depth"]
    labels = [
        "Blood Vessel Density (%)",
        "Max Blood Vessel Diameter ($\mu$m)",
        "Plexus Depth ($\mu$m)",
    ]

    # Variants: raw + both outlier approaches
    variants = [
        {"name": "raw", "method": None, "Q": 0.01, "multiplier": 1.5},
        {"name": "rout_Q001", "method": "rout", "Q": 0.01, "multiplier": 1.5},
        {"name": "iqr_1p5", "method": "iqr", "Q": 0.01, "multiplier": 1.5},
    ]

    for data_type, label in zip(data_types, labels):
        (
            combined_data_by_exposure,
            combined_data_by_location,
        ) = collector.combine_subject_data_by_location(
            subject_data, "blood_data", data_type
        )

        for v in variants:
            method = v["method"]
            variant_name = v["name"]

            if method is None:
                loc_data = combined_data_by_location
                exp_data = combined_data_by_exposure
            else:
                loc_data = outliers._clean_location_data(
                    combined_data_by_location,
                    method=method,
                    Q=v["Q"],
                    multiplier=v["multiplier"],
                )
                exp_data = outliers._clean_exposure_data(
                    combined_data_by_exposure,
                    method=method,
                    Q=v["Q"],
                    multiplier=v["multiplier"],
                )

            stats_by_loc = all_subjects_data_collector.compute_box_stats_by_location(
                loc_data
            )
            exposure_stats = all_subjects_data_collector.compute_box_stats_by_exposure(
                exp_data
            )

            data_type_tag = f"{data_type}_{variant_name}"

            plotting.plot_box_by_location(
                loc_data,
                stats_by_loc,
                data_type_tag,
                label,
                plot_dir,
            )
            plotting.plot_box_by_location_exposure(
                exp_data,
                exposure_stats,
                data_type_tag,
                label,
                plot_dir,
            )
