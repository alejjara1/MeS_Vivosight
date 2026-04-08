import os
import plotting
import all_subjects_data_collector


def run_plots(collector, subject_data, data_dict, plot_dir, data_types, labels):
    """
    Run the full plotting and stats pipeline for one data category.

    Args:
        collector: AllSubjectsDataCollector instance (already loaded)
        subject_data: dict returned by get_X_data()
        data_dict: visit attribute name, e.g. "inflection_depths"
        plot_dir: root output directory for this category
        data_types: list of measurement names to iterate over
        labels: list of y-axis labels matching data_types
    """
    os.makedirs(plot_dir, exist_ok=True)
    all_sig_results = {}

    for data_type, label in zip(data_types, labels):

        data_plot_dir = plot_dir + data_type + "/"
        os.makedirs(data_plot_dir, exist_ok=True)

        average_data_by_exposure = collector.collect_averaged_data_by_exposure(
            subject_data, data_dict, data_type
        )

        plotting.plot_depth_by_location(
            average_data_by_exposure, data_plot_dir, data_type
        )
        plotting.plot_depth_by_location_exposure(
            average_data_by_exposure, data_plot_dir, data_type, label_points=False
        )

        combined_data_by_exposure, combined_data_by_location = (
            collector.collect_difference_by_location_exposure(
                subject_data, data_dict, data_type
            )
        )

        stats_by_loc = all_subjects_data_collector.compute_box_stats_by_location(
            combined_data_by_location
        )
        exposure_stats = all_subjects_data_collector.compute_box_stats_by_exposure(
            combined_data_by_exposure
        )

        all_sig_results[data_type] = {
            "stats_by_loc": stats_by_loc,
            "exposure_stats": exposure_stats,
            "combined_data_by_location": combined_data_by_location,
            "combined_data_by_exposure": combined_data_by_exposure,
        }

        plotting.plot_box_by_location(
            combined_data_by_location,
            stats_by_loc,
            data_type,
            label,
            data_plot_dir,
        )
        plotting.plot_box_by_location_exposure(
            combined_data_by_exposure,
            exposure_stats,
            data_type,
            label,
            data_plot_dir,
        )

    all_subjects_data_collector.write_significant_results(
        plot_dir + "significant_results.txt",
        all_sig_results,
    )

    return all_sig_results


if __name__ == "__main__":

    # --- Shared configuration ---
    vivosight_folder = "data/Vivosight_data/"
    scan_folder = "data/scan_information/"
    file_subject_codes = "data/SubjectCodes.xlsx"
    subject_id_skip = ["E50", "Leena", "R22", "E11"]
    subject_id_swap = {"Z47": "Z65"}

    collector = all_subjects_data_collector.AllSubjectsDataCollector(
        vivosight_folder=vivosight_folder,
        scan_folder=scan_folder,
        subject_codes_file=file_subject_codes,
        subject_id_skip=subject_id_skip,
    )
    collector.get_subject_ids()
    collector.get_subject_codes(subject_id_swap)

    # --- Per-category config: (category_name, get_data_fn, data_dict, plot_dir, data_types, labels) ---
    categories = [
        (
            "Epidermal",
            lambda: collector.get_epidermal_data(approach=0),
            "inflection_depths",
            "../data_out/epidermal/",
            ["depth", "attenuation_coeff"],
            ["Epidermal thickness ($\\mu$m)", "Attenuation Coefficient (mm$^{-1}$)"],
        ),
        (
            "Blood Flow",
            collector.get_bloodflow_data,
            "blood_data",
            "../data_out/bloodflow/",
            ["max_density", "max_diameter", "plexus_depth"],
            [
                "Blood Vessel Density (%)",
                "Max Blood Vessel Diameter ($\\mu$m)",
                "Plexus Depth ($\\mu$m)",
            ],
        ),
        (
            "Skin Roughness",
            collector.get_skin_roughness_data,
            "skin_roughness_data",
            "../data_out/skin_roughness/",
            ["Ra", "Rz", "Rq"],
            ["Ra ($\\mu$m)", "Rz ($\\mu$m)", "Rq ($\\mu$m)"],
        ),
        (
            "Skin Surface",
            collector.get_skin_surface_data,
            "skin_surface_data",
            "../data_out/skin_surface/",
            ["surface_area"],
            ["Skin Surface Area Ratio (-)"],
        ),
    ]

    combined_sig_results = {}

    for category_name, get_data, data_dict, plot_dir, data_types, labels in categories:
        print(f"\n{'=' * 50}\nProcessing: {category_name}\n{'=' * 50}")
        subject_data = get_data()
        sig_results = run_plots(
            collector, subject_data, data_dict, plot_dir, data_types, labels
        )
        for data_type, result in sig_results.items():
            combined_sig_results[f"{category_name} / {data_type}"] = result

    all_subjects_data_collector.write_significant_results(
        "../data_out/significant_results_all.txt",
        combined_sig_results,
    )
