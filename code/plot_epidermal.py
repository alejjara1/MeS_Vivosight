import os
import plotting
import all_subjects_data_collector


if __name__ == "__main__":

    plot_dir = "../data_out/epidermal/"
    os.makedirs(plot_dir, exist_ok=True)

    tewl_scatter_dir = plot_dir + "tewl_scatter/"
    os.makedirs(tewl_scatter_dir, exist_ok=True)

    # scatter_plot_dir = "../data_out/epidermal/scatter/"
    # os.makedirs(scatter_plot_dir, exist_ok=True)

    # Data input location
    vivosight_folder = "data/Vivosight_data/"
    scan_folder = "data/scan_information/"
    tewl_folder = "data/TEWL_Data/"
    file_subject_codes = "data/SubjectCodes.xlsx"

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

    # Read data and depths
    subject_data = collector.get_epidermal_data(approach=0)
    tewl_subject_data = collector.get_tewl_data()
    tewl_average = collector.get_tewl_average(tewl_subject_data, 1)

    # Save depth data
    # collector.save_inflection_depths(subject_data, plot_dir + "inflection_depths/")

    ##### Plots #####
    data_types = ["depth", "attenuation_coeff", "sid", "AuC"]
    labels = [
        "Epidermal Thickness ($\\mu$m)",
        "Attenuation Coefficient (mm$^{-1}$)",
        "Scaled Intensity Drop (mm)",
        "Area Under Curve (dB-mm)",
    ]

    all_sig_results = {}
    all_subject_diff = {}

    for data_type, label in zip(data_types, labels):

        data_plot_dir = plot_dir + data_type + "/"
        os.makedirs(data_plot_dir, exist_ok=True)

        subject_diff = collector.get_visit_average_exposed_diff(
            subject_data, "epidermal_data", data_type
        )
        all_subject_diff[label] = subject_diff

        # Data exploration
        average_data_by_exposure = collector.collect_averaged_data_by_exposure(
            subject_data, "epidermal_data", data_type
        )

        plotting.plot_data_by_location(
            average_data_by_exposure, data_plot_dir, data_type, label
        )
        plotting.plot_data_by_location_exposure(
            average_data_by_exposure,
            data_plot_dir,
            data_type,
            label,
            label_points=False,
        )

        # Statistics
        combined_data_by_exposure, combined_data_by_location = (
            collector.collect_difference_by_location_exposure(
                subject_data, "epidermal_data", data_type, combine_locations=True
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
            combine_locations_1_2=True,
        )
        plotting.plot_box_by_location_exposure(
            combined_data_by_exposure,
            exposure_stats,
            data_type_tag,
            label,
            data_plot_dir,
            combine_locations_1_2=True,
        )

        plotting.plot_subject_diff_vs_tewl(
            subject_diff,
            tewl_average,
            tewl_scatter_dir + f"tewl_vs_{data_type}.pdf",
            x_label="Average TEWL (g/m$^2$-h) at location 1",
            y_label=f"$\\Delta$ {label}",
        )

    plotting.plot_subject_diff_heatmap(
        all_subject_diff,
        plot_dir + "subject_diff_heatmap.pdf",
        title="Subject Difference Heatmap Across Epidermal Parameters",
    )

    all_subjects_data_collector.write_significant_results(
        plot_dir + "significant_results.txt",
        all_sig_results,
    )

    # depth_by_exposure = collector.combine_data_by_exposure(
    #     subject_data, "epidermal_data", "depth"
    # )

    # sid_by_exposure = collector.combine_data_by_exposure(
    #     subject_data, "epidermal_data", "sid", "depth"
    # )

    # auc_by_exposure = collector.combine_data_by_exposure(
    #     subject_data, "epidermal_data", "AuC", "depth"
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
