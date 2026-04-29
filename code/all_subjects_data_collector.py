import data_read
import TEWL
import numpy as np
from scipy import stats
import glob
import pandas as pd


def compute_pre_post_wilcoxon_stats(pre_vals, post_vals, context_label):
    """
    Compute Wilcoxon statistics for pre vs post measurements.

    Args:
        pre_vals: List of pre-exposure values
        post_vals: List of post-exposure values
        context_label: String label for context (printed with results)

    Returns:
        Tuple of (p_value, significance_star) or (None, None) if insufficient data
    """
    min_len = min(len(pre_vals), len(post_vals))
    if min_len < 2:
        return None, None

    stat_pre = pre_vals[:min_len]
    stat_post = post_vals[:min_len]
    _, p_val = stats.wilcoxon(stat_pre, stat_post)

    if np.isnan(p_val):
        return None, None

    if p_val < 0.001:
        star = "***"
    elif p_val < 0.01:
        star = "**"
    elif p_val < 0.05:
        star = "*"
    else:
        star = "ns"

    print(
        f"Wilcoxon stats | context={context_label} | N={min_len} "
        f"(pre={len(pre_vals)}, post={len(post_vals)}) | p={p_val:.4g} | star={star}"
    )

    return p_val, star


def compute_wilcoxon_stats(diff_vals, context_label):
    """
    Compute Wilcoxon signed-rank test statistics for difference values.
    Args:
        diff_vals: List of difference values (post - pre)
        context_label: String label for context (printed with results)
    Returns:
        Tuple of (p_value, significance_star) or (None, None) if insufficient data
    """
    if len(diff_vals) < 2:
        return None, None

    _, p_val = stats.wilcoxon(diff_vals)

    if np.isnan(p_val):
        return None, None

    if p_val < 0.001:
        star = "***"
    elif p_val < 0.01:
        star = "**"
    elif p_val < 0.05:
        star = "*"
    else:
        star = "ns"

    # print(
    #     f"Wilcoxon stats | context={context_label} | N={len(diff_vals)} | p={p_val:.4g} | star={star}"
    # )
    return p_val, star


def compute_box_stats_by_location(data_by_loc):
    """
    Compute Wilcoxon statistics for data by location.

    Args:
        data_by_loc: Dict with structure {loc: {"pre": [], "post": []}}

    Returns:
        Dict with structure {loc: {"p_val": float, "star": str}}
    """
    stats_by_loc = {}

    locations = data_by_loc.keys()

    for loc in locations:
        diff_vals = data_by_loc[loc]["diff"]
        p_val, star = compute_wilcoxon_stats(
            diff_vals, context_label=f"all | location={loc}"
        )
        if p_val is not None:
            stats_by_loc[loc] = {"p_val": p_val, "star": star}

    return stats_by_loc


def compute_box_stats_by_exposure(exposure_data):
    """
    Compute Wilcoxon statistics for data by exposure and location.

    Args:
        exposure_data: Dict with structure {exposure: {"pre": {loc: []}, "post": {loc: []}}}

    Returns:
        Dict with structure {exposure: {loc: {"p_val": float, "star": str}}}
    """
    exposure_stats = {}

    locations = next(iter(exposure_data.values()))["diff"].keys()

    for exposure in DataFactory.EXPOSURES:
        exposure_stats[exposure] = {}
        for loc in locations:
            diff_vals = exposure_data[exposure]["diff"][loc]
            p_val, star = compute_wilcoxon_stats(
                diff_vals,
                context_label=f"exposure={exposure} | location={loc}",
            )
            if p_val is not None:
                exposure_stats[exposure][loc] = {"p_val": p_val, "star": star}

    return exposure_stats


def write_significant_results(path, all_results):
    """
    Write a single summary of significant Wilcoxon results across all data types.

    Args:
        path: output file path
        all_results: dict {data_type: {stats_by_loc, exposure_stats,
                                       combined_data_by_location, combined_data_by_exposure}}
    """
    lines = []
    lines.append("Significant Results Summary")
    lines.append("=" * 50)

    def _ordered_locations(location_dict):
        preferred = [1, 2, "1+2", 3, 4]
        ordered = [loc for loc in preferred if loc in location_dict]
        extras = [loc for loc in location_dict if loc not in preferred]
        ordered.extend(extras)
        return ordered

    for data_type, r in all_results.items():
        stats_by_loc = r["stats_by_loc"]
        exposure_stats = r["exposure_stats"]
        combined_data_by_location = r["combined_data_by_location"]
        combined_data_by_exposure = r["combined_data_by_exposure"]
        tewl_r_squared = r.get("tewl_r_squared")

        lines.append("")
        lines.append(f"Variable: {data_type}")
        lines.append("-" * 50)
        if tewl_r_squared is not None:
            lines.append(f"  TEWL vs Δ{data_type}: R² = {tewl_r_squared:.4f}")
        else:
            lines.append(f"  TEWL vs Δ{data_type}: R² = N/A")

        lines.append("  By Location (all exposures combined)")
        any_sig = False
        for loc in _ordered_locations(stats_by_loc):
            s = stats_by_loc[loc]
            if s["star"] == "ns":
                continue
            n = len(combined_data_by_location[loc]["diff"])
            lines.append(
                f"    Location {loc}: N={n:>2},  p={s['p_val']:.4g},  {s['star']}"
            )
            any_sig = True
        if not any_sig:
            lines.append("    (none)")

        lines.append("")
        lines.append("  By Location and Exposure")
        any_sig_exp = False
        for exposure in ["Low", "Med", "High"]:
            loc_stats = exposure_stats.get(exposure, {})
            for loc in _ordered_locations(loc_stats):
                s = loc_stats[loc]
                if s["star"] == "ns":
                    continue
                n = len(combined_data_by_exposure[exposure]["diff"][loc])
                lines.append(
                    f"    {exposure:<4} - Location {loc}: N={n:>2},  p={s['p_val']:.4g},  {s['star']}"
                )
                any_sig_exp = True
        if not any_sig_exp:
            lines.append("    (none)")

    lines.append("")

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Significant results written to {path}")


class DataFactory:
    """Factory for creating repetitive data structures based on locations and exposure levels."""

    LOCATIONS = [1, 2, 3, 4]
    EXPOSURES = ["Low", "Med", "High"]

    @staticmethod
    def create_by_location(default_value_factory=list):
        """Create a dict with location keys (1-4) and default values."""
        return {loc: default_value_factory() for loc in DataFactory.LOCATIONS}

    @staticmethod
    def create_by_exposure(value_factory):
        """Create a dict with exposure keys and values from factory function."""
        return {exp: value_factory() for exp in DataFactory.EXPOSURES}

    @staticmethod
    def create_by_exposure_and_location(default_value_factory=list):
        """Create nested dict: exposure -> location -> default value."""
        return DataFactory.create_by_exposure(
            lambda: DataFactory.create_by_location(default_value_factory)
        )

    @staticmethod
    def create_scatter_data():
        """Create dict for scatter plot data: exposure -> {x_key: [], y_key: []}."""
        return DataFactory.create_by_exposure(lambda: {"depth": [], "sid": []})

    @staticmethod
    def create_scatter_data_with_keys(key1, key2):
        """Create dict for scatter plot with custom keys."""
        return DataFactory.create_by_exposure(lambda: {key1: [], key2: []})


class AllSubjectsDataCollector:
    """
    Manages data collection and storage for all subjects across various plot types.
    Collects depth data, boxplot data, and scatter data from subject visits.
    """

    def __init__(
        self,
        vivosight_folder,
        scan_folder,
        tewl_folder,
        subject_codes_file,
        subject_id_skip,
    ):

        self.vivosight_folder = vivosight_folder
        self.scan_folder = scan_folder
        self.tewl_folder = tewl_folder
        self.subject_codes_file = subject_codes_file
        self.subject_id_skip = subject_id_skip
        self.subject_ids = None
        self.subject_codes = None

    def collect_averaged_data_by_exposure(self, subject_data, data_dict, data_source):
        """
        Generic function to collect averaged data by exposure level.

        Returns:
            Dictionary with structure: {exposure: {subject_id: {loc: {"pre": value, "post": value}}}}
            or empty dict if subject should be skipped
        """
        result = {}

        for subject_id in self.subject_ids:
            visit = subject_data[subject_id].visit
            exposure = self.subject_codes[subject_id]["exposure"]

            if exposure not in result:
                result[exposure] = {}

            result[exposure][subject_id] = {}

            for loc in DataFactory.LOCATIONS:
                loc_data = getattr(visit, data_dict)[loc]
                pre = loc_data.get_pre_average(data_source)
                post = loc_data.get_post_average(data_source)

                if pre is None or post is None:
                    diff = None
                else:
                    diff = post - pre
                loc_values = {"pre": pre, "post": post, "diff": diff}
                result[exposure][subject_id][loc] = loc_values

        return result

    def collect_difference_by_location_exposure(
        self, subject_data, data_dict, data_source, combine_locations=False
    ):
        """Determine difference between paired pre/post subject averages by location and exposure."""
        result_exposure_location = DataFactory.create_by_exposure(
            lambda: {
                "diff": DataFactory.create_by_location(),
            }
        )
        result_location = {loc: {"diff": []} for loc in DataFactory.LOCATIONS}

        if combine_locations:
            result_location["1+2"] = {"diff": []}

        for subject_id in self.subject_ids:
            visit = subject_data[subject_id].visit
            exposure = self.subject_codes[subject_id]["exposure"]

            for loc in DataFactory.LOCATIONS:
                loc_data = getattr(visit, data_dict)[loc]
                pre_val = loc_data.get_pre_average(data_source)
                post_val = loc_data.get_post_average(data_source)

                # keep only complete, valid pairs
                if pre_val is None or post_val is None:
                    continue
                if not (np.isfinite(pre_val) and np.isfinite(post_val)):
                    continue

                diff = float(post_val) - float(pre_val)
                result_location[loc]["diff"].append(diff)

                result_exposure_location[exposure]["diff"][loc].append(diff)

            if combine_locations:
                result_exposure_location[exposure]["diff"]["1+2"] = (
                    result_exposure_location[exposure]["diff"][1]
                    + result_exposure_location[exposure]["diff"][2]
                )

                result_location["1+2"]["diff"] = (
                    result_location[1]["diff"] + result_location[2]["diff"]
                )

        return result_exposure_location, result_location

    def combine_data_by_exposure(
        self, subject_data, data_dict, data_source, restrict_data_source=None
    ):
        """
        Combine pre and post measurements by exposure level, flattening across all locations.

        This method aggregates data from all subjects and locations into simple pre/post lists
        grouped by exposure level. Each data point is filtered to ensure validity before
        being included in the results.

        Args:
            subject_data: Dict mapping subject_id to Subject objects with visit data
            data_dict: String name of the visit attribute containing location data
                      (e.g., "epidermal_data")
            data_source: String name of the attribute to extract from each measurement
                        (e.g., "depth", "sid", "AuC")
            restrict_data_source: Optional string name of an attribute to use for filtering.
                                 If provided, data points are only included if both data_source
                                 and restrict_data_source are non-None and > 0.
                                 If None, only data_source is checked for validity.
                                 (e.g., "depth" to filter out measurements where depth <= 0)

        Returns:
            Dictionary with structure: {exposure: {"pre": [values], "post": [values]}}
            where exposure is "Low", "Med", or "High", and values are the filtered
            measurements aggregated across all subjects and locations.

        Example:
            >>> depth_by_exposure = collector.combine_data_by_exposure(
            ...     subject_data, "epidermal_data", "depth"
            ... )
            >>> sid_by_exposure = collector.combine_data_by_exposure(
            ...     subject_data, "epidermal_data", "sid", restrict_data_source="depth"
            ... )
        """

        result_exposure = DataFactory.create_by_exposure(
            lambda: {
                "pre": [],
                "post": [],
            }
        )
        for subject_id in self.subject_ids:
            visit = subject_data[subject_id].visit
            exposure = self.subject_codes[subject_id]["exposure"]
            for loc in DataFactory.LOCATIONS:
                loc_data = getattr(visit, data_dict)[loc]
                pre_vals = [
                    getattr(p, data_source)
                    for p in loc_data.pre
                    if getattr(p, data_source) is not None
                    and getattr(p, data_source) > 0
                    and (
                        restrict_data_source is None
                        or (
                            getattr(p, restrict_data_source) is not None
                            and getattr(p, restrict_data_source) > 0
                        )
                    )
                ]
                post_vals = [
                    getattr(p, data_source)
                    for p in loc_data.post
                    if getattr(p, data_source) is not None
                    and getattr(p, data_source) > 0
                    and (
                        restrict_data_source is None
                        or (
                            getattr(p, restrict_data_source) is not None
                            and getattr(p, restrict_data_source) > 0
                        )
                    )
                ]
                result_exposure[exposure]["pre"].extend(pre_vals)
                result_exposure[exposure]["post"].extend(post_vals)
        return result_exposure

    def get_subject_ids(self, separate_return_visit=True, skip_returns=False):
        """
        Collects the subject IDs
        """
        self.subject_ids = data_read.get_all_subject_ids(
            self.vivosight_folder, separate_return_visit, skip_returns
        )
        for skip in self.subject_id_skip:
            if skip in self.subject_ids:
                self.subject_ids.remove(skip)

    def get_subject_codes(self, subject_id_swap):
        """
        Collect and modifies subject codes
        """
        self.subject_codes = data_read.read_subject_codes_and_doses(
            self.subject_codes_file
        )
        for old_id, new_id in subject_id_swap.items():
            if new_id in self.subject_codes:
                self.subject_codes[old_id] = self.subject_codes[new_id]

    def get_epidermal_data(self, approach=0, plot=False):
        """
        Collect epidermal data
        """
        subject_data = {}
        for subject_id in self.subject_ids:

            subject_data[subject_id] = data_read.process_subject_vivosight_data(
                subject_id,
                self.vivosight_folder,
                self.scan_folder,
                "epidermal",
                merge_return=False,
                exposure=self.subject_codes[subject_id]["exposure"],
            )

            subject_data[subject_id].visit.collect_epidermal_data(
                approach=approach, plot=plot
            )

        return subject_data

    def save_inflection_depths(self, subject_data, output_dir):
        """
        Save inflection depth data
        """
        for subject_id in self.subject_ids:
            subject_data[subject_id].visit.save_inflection_data_to_file(output_dir)

    def get_bloodflow_data(self):
        """
        Collect blood flow data
        """
        subject_data = {}
        for subject_id in self.subject_ids:

            subject_data[subject_id] = data_read.process_subject_vivosight_data(
                subject_id,
                self.vivosight_folder,
                self.scan_folder,
                "bloodflow",
                merge_return=False,
                exposure=self.subject_codes[subject_id]["exposure"],
            )

            subject_data[subject_id].visit.collect_blood_scans()

        return subject_data

    def get_skin_roughness_data(self):
        """
        Collect skin roughness data
        """
        subject_data = {}
        for subject_id in self.subject_ids:
            subject_data[subject_id] = data_read.process_subject_vivosight_data(
                subject_id,
                self.vivosight_folder,
                self.scan_folder,
                "skin roughness",
                merge_return=False,
                exposure=self.subject_codes[subject_id]["exposure"],
            )

            subject_data[subject_id].visit.collect_skin_roughness_scans()

        return subject_data

    def get_skin_surface_data(self):
        """
        Collect skin surface data
        """
        subject_data = {}
        for subject_id in self.subject_ids:

            subject_data[subject_id] = data_read.process_subject_vivosight_data(
                subject_id,
                self.vivosight_folder,
                self.scan_folder,
                "surface area",
                merge_return=False,
                exposure=self.subject_codes[subject_id]["exposure"],
            )

            subject_data[subject_id].visit.collect_skin_surface_scans()

        return subject_data

    def get_tewl_data(self):
        """
        Collect tewl data
        """
        subject_data = {}
        files_tewl_raw = glob.glob(f"{self.tewl_folder}*.xls")
        for file in files_tewl_raw:
            subject_id = TEWL.collect_subject_id_from_file(file)
            if subject_id in self.subject_id_skip:
                continue
            new_subject_id = self.subject_codes[subject_id]["new_pid"]

            new_subject_id = new_subject_id.split("_")[0]

            location = TEWL.collect_location_from_file(file)
            return_visit = TEWL.collect_return_visit_from_file(file)

            data = pd.read_excel(file)
            if subject_id not in subject_data:
                subject_data[subject_id] = TEWL.Subject(subject_id=new_subject_id)

            subject_data[subject_id].add_scan(
                location=location,
                return_visit=return_visit,
                data=data,
            )

            subject_data[subject_id].set_averages()

        return subject_data

    def get_tewl_average(self, tewl_subject_data, location):
        """Get the average tewl for all subjects at specified location"""
        subject_data = {}
        for subject_id, subject in tewl_subject_data.items():
            subject_data[subject_id] = subject.get_average(location)

        return subject_data

    def get_visit_diff_data(self, visit_subject_data, data_dict, data_source, location):
        """Get the difference data at location"""
        subject_data = {}
        for subject_id, subject in visit_subject_data.items():
            loc_data = getattr(subject.visit, data_dict)[location]
            pre_val = loc_data.get_pre_average(data_source)
            post_val = loc_data.get_post_average(data_source)

            if (
                pre_val is None
                or post_val is None
                or not np.isfinite(pre_val)
                or not np.isfinite(post_val)
            ):
                subject_data[subject_id] = None
            else:
                subject_data[subject_id] = float(post_val) - float(pre_val)

        return subject_data

    def get_visit_average_exposed_diff(
        self, visit_subject_data, data_dict, data_source
    ):
        """Determine the average difference from the two exposed locations"""
        diff_1 = self.get_visit_diff_data(visit_subject_data, data_dict, data_source, 1)
        diff_2 = self.get_visit_diff_data(visit_subject_data, data_dict, data_source, 2)

        subject_data = {}
        for subject_id in visit_subject_data:
            loc_diffs = [
                d
                for d in (diff_1.get(subject_id), diff_2.get(subject_id))
                if d is not None
            ]
            subject_data[subject_id] = float(np.mean(loc_diffs)) if loc_diffs else None

        return subject_data
