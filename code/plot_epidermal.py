import os
import plotting
import outliers
import all_subjects_data_collector


if __name__ == "__main__":

    plot_dir = "../data_out/epidermal/"
    os.makedirs(plot_dir, exist_ok=True)

    # scatter_plot_dir = "../data_out/epidermal/scatter/"
    # os.makedirs(scatter_plot_dir, exist_ok=True)

    # Data input location
    vivosight_folder = "data/Vivosight_data/"
    scan_folder = "data/scan_information/"
    file_subject_codes = "data/SubjectCodes.xlsx"

    # Subje ct id modifications
    subject_id_skip = ["E50", "Leena", "R22", "E11"]
    subject_id_swap = {"Z47": "Z65"}

    # Collect depth data for plotting, boxplot data, and scatter data
    collector = all_subjects_data_collector.AllSubjectsDataCollector(
        vivosight_folder=vivosight_folder,
        scan_folder=scan_folder,
        subject_codes_file=file_subject_codes,
        subject_id_skip=subject_id_skip,
    )

    collector.get_subject_ids()
    collector.get_subject_codes(subject_id_swap)

    # Read data and depths
    subject_data = collector.get_epidermal_data(approach=0)

    # Save depth data
    # collector.save_inflection_depths(subject_data, plot_dir + "inflection_depths/")

    ##### Plots #####
    data_types = ["depth", "attenuation_coeff"]
    labels = ["Epidermal thickness ($\mu$m)", "Attenuation Coefficient (mm$^{-1}$)"]

    all_sig_results = {}

    for data_type, label in zip(data_types, labels):

        data_plot_dir = plot_dir + data_type + "/"
        os.makedirs(data_plot_dir, exist_ok=True)

        # Data exploration
        average_depth_data_by_exposure = collector.collect_averaged_data_by_exposure(
            subject_data, "inflection_depths", data_type
        )

        plotting.plot_depth_by_location(
            average_depth_data_by_exposure, data_plot_dir, data_type
        )
        plotting.plot_depth_by_location_exposure(
            average_depth_data_by_exposure, data_plot_dir, data_type, label_points=False
        )

        # Statistics
        combined_data_by_exposure, combined_data_by_location = (
            collector.collect_difference_by_location_exposure(
                subject_data, "inflection_depths", data_type
            )
        )

        stats_by_loc = all_subjects_data_collector.compute_box_stats_by_location(
            combined_data_by_location
        )

        exposure_stats = all_subjects_data_collector.compute_box_stats_by_exposure(
            combined_data_by_exposure
        )

        data_type_tag = f"{data_type}"

        all_sig_results[data_type] = {
            "stats_by_loc": stats_by_loc,
            "exposure_stats": exposure_stats,
            "combined_data_by_location": combined_data_by_location,
            "combined_data_by_exposure": combined_data_by_exposure,
        }

        plotting.plot_box_by_location(
            combined_data_by_location,
            stats_by_loc,
            data_type_tag,
            label,
            data_plot_dir,
        )
        plotting.plot_box_by_location_exposure(
            combined_data_by_exposure,
            exposure_stats,
            data_type_tag,
            label,
            data_plot_dir,
        )

    all_subjects_data_collector.write_significant_results(
        plot_dir + "significant_results.txt",
        all_sig_results,
    )

    # depth_by_exposure = collector.combine_data_by_exposure(
    #     subject_data, "inflection_depths", "depth"
    # )

    # sid_by_exposure = collector.combine_data_by_exposure(
    #     subject_data, "inflection_depths", "sid", "depth"
    # )

    # auc_by_exposure = collector.combine_data_by_exposure(
    #     subject_data, "inflection_depths", "AuC", "depth"
    # )

    # plotting.plot_scatter_by_exposure(
    #     depth_by_exposure,
    #     sid_by_exposure,
    #     "Epidermal Thickness ($\mu$m)",
    #     "SID",
    #     scatter_plot_dir + "depth_vs_sid.pdf",
    # )
    # plotting.plot_scatter_by_exposure(
    #     depth_by_exposure,
    #     auc_by_exposure,
    #     "Epidermal Thickness ($\mu$m)",
    #     "AUC",
    #     scatter_plot_dir + "auc_vs_depth.pdf",
    # )
    # plotting.plot_scatter_by_exposure(
    #     sid_by_exposure,
    #     auc_by_exposure,
    #     "SID",
    #     "AUC",
    #     scatter_plot_dir + "sid_vs_auc.pdf",
    # )
