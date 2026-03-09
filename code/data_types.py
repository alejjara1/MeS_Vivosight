import pandas as pd
import Epidermal
import Bloodflow
import SkinRoughness
import SkinSurface


class Subject:
    def __init__(self, subject_id, exposure):
        self.subject_id = subject_id
        self.exposure = exposure
        self.visit = None
        self.return_visit = None


class Visit:
    def __init__(self, subject):
        self.subject = subject
        self.scans = None
        self.skin_roughness = None
        self.epidermal = []
        self.blood_flow = []
        self.skin_roughness = []
        self.skin_surface = []
        self.num_scans = 0
        self.num_skin_roughness = 0
        self.num_skin_surface = 0
        self.num_epidermal = 0
        self.num_blood_flow = 0
        self.before_scan_id = None
        self.before_locations = None
        self.after_locations = None
        self.after_scan_id = None
        self.inflection_depths = {
            1: Epidermal.LocationData(),
            2: Epidermal.LocationData(),
            3: Epidermal.LocationData(),
            4: Epidermal.LocationData(),
        }
        self.blood_data = {
            1: Bloodflow.LocationData(),
            2: Bloodflow.LocationData(),
            3: Bloodflow.LocationData(),
            4: Bloodflow.LocationData(),
        }
        self.skin_roughness_data = {
            1: SkinRoughness.LocationData(),
            2: SkinRoughness.LocationData(),
            3: SkinRoughness.LocationData(),
            4: SkinRoughness.LocationData(),
        }
        self.skin_surface_data = {
            1: SkinSurface.LocationData(),
            2: SkinSurface.LocationData(),
            3: SkinSurface.LocationData(),
            4: SkinSurface.LocationData(),
        }

    def add_skin_roughness(self, skin_roughness_data):
        """
        skin roughness function
        """
        if self.skin_roughness is None:
            self.skin_roughness = []

        self.skin_roughness.append(skin_roughness_data)

        self.num_skin_roughness += 1

    def add_skin_surface(self, skin_surface_data):
        """
        skin roughness function
        """
        if self.skin_surface is None:
            self.skin_surface = []

        self.skin_surface.append(skin_surface_data)

        self.num_skin_surface += 1

    def add_epidermal(self, epidermal_data):
        """
        epidermal data function
        """
        self.epidermal.append(epidermal_data)

        self.num_epidermal += 1

    def collect_epidermal_data(self, approach=0, plot=False):
        """
        Collect epidermal depth in convenient dictionary
        """
        for derm_scan in self.epidermal:
            if derm_scan.location not in [1, 2, 3, 4]:
                print(
                    f"Subject ID {self.subject.subject_id} Invalid location: {derm_scan.location}"
                )
                continue

            self.inflection_depths = derm_scan.get_epidermal_data(
                self.inflection_depths, approach
            )

            if plot:
                derm_scan.plot_a_scan(self.subject.subject_id)

    def collect_blood_scans(self):
        """
        Collect blood scan data in convenient dictionary
        """
        for b_scan in self.blood_flow:
            if b_scan.location not in [1, 2, 3, 4]:
                print(
                    f"Subject ID {self.subject.subject_id} Invalid location: {b_scan.location}"
                )
                continue

            self.blood_data = b_scan.set_blood_scan_data(self.blood_data)

    def collect_skin_roughness_scans(self):
        """
        Collect skin roughness data in convenient dictionary
        """
        for s_scan in self.skin_roughness:
            if s_scan.location not in [1, 2, 3, 4]:
                print(
                    f"Subject ID {self.subject.subject_id} Invalid location: {s_scan.location}"
                )
                continue

            self.skin_roughness_data = s_scan.get_skin_roughness_data(
                self.skin_roughness_data
            )

    def collect_skin_surface_scans(self):
        """
        Collect skin roughness data in convenient dictionary
        """
        for s_scan in self.skin_surface:
            if s_scan.location not in [1, 2, 3, 4]:
                print(
                    f"Subject ID {self.subject.subject_id} Invalid location: {s_scan.location}"
                )
                continue

            self.skin_surface_data = s_scan.get_skin_surface_data(
                self.skin_surface_data
            )

    def get_all_location_averages(self):
        """
        Calculate pre and post averages for all locations.

        Returns:
            dict: Dictionary with location as key and dict of pre/post averages as value
        """
        averages = {}
        for location in [1, 2, 3, 4]:
            averages[location] = {
                "pre": self.inflection_depths[location].get_pre_average(),
                "post": self.inflection_depths[location].get_post_average(),
            }
        return averages

    def save_inflection_data_to_file(self, output_dir):
        """
        Save all inflection depth data to a text file organized by subject ID.

        Args:
            output_dir: Directory to save the output files
        """
        import os

        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/{self.subject.subject_id}_inflection_depths.txt"

        with open(filename, "w") as f:
            f.write(f"Subject ID: {self.subject.subject_id}\n")
            f.write(f"Exposure: {self.subject.exposure}\n")
            f.write("=" * 60 + "\n\n")

            for location in [1, 2, 3, 4]:
                f.write(f"Location {location}:\n")
                f.write("-" * 40 + "\n")

                loc_data = self.inflection_depths[location]

                # Pre-exposure data
                f.write("  Pre-Exposure:\n")
                if loc_data.pre:
                    for i, point in enumerate(loc_data.pre, 1):
                        depth_str = (
                            f"{point.depth:.4f} mm"
                            if point.depth and point.depth > 0
                            else "N/A"
                        )
                        f.write(
                            f"    {i}. Depth: {depth_str}, Approach: {point.approach}, Scan ID: {point.scan_id}\n"
                        )
                    pre_avg = loc_data.get_pre_average()
                    pre_str = f"{pre_avg:.4f} mm" if pre_avg is not None else "N/A"
                    f.write(f"    Average: {pre_str}\n")
                else:
                    f.write("    No data\n")

                f.write("\n")

                # Post-exposure data
                f.write("  Post-Exposure:\n")
                if loc_data.post:
                    for i, point in enumerate(loc_data.post, 1):
                        depth_str = (
                            f"{point.depth:.4f} mm"
                            if point.depth and point.depth > 0
                            else "N/A"
                        )
                        f.write(
                            f"    {i}. Depth: {depth_str}, Approach: {point.approach}, Scan ID: {point.scan_id}\n"
                        )
                    post_avg = loc_data.get_post_average()
                    post_str = f"{post_avg:.4f} mm" if post_avg is not None else "N/A"
                    f.write(f"    Average: {post_str}\n")
                else:
                    f.write("    No data\n")

                f.write("\n")

            # Summary averages
            f.write("\nSummary - All Locations Averages:\n")
            f.write("=" * 60 + "\n")
            averages = self.get_all_location_averages()
            for location, avgs in averages.items():
                pre_str = f"{avgs['pre']:.4f}" if avgs["pre"] is not None else "N/A"
                post_str = f"{avgs['post']:.4f}" if avgs["post"] is not None else "N/A"
                f.write(f"Location {location}: Pre={pre_str} mm, Post={post_str} mm\n")

        print(f"Data saved to: {filename}")

    def add_blood_flow(self, blood_flow_data):
        """
        blood flow data function
        """
        self.blood_flow.append(blood_flow_data)
        self.num_blood_flow += 1

    def process_subject_scan_data(self, file: str, return_visit: bool):
        """ """
        try:
            before_exposure_data = pd.read_excel(file, "Surface Area_BE")
            after_exposure_data = pd.read_excel(file, "Surface Area_AE")
        except Exception as reason:
            print(
                f"There is an issue with \t {file}. \t This data will be excluded from the analysis. Reason: {reason}"
            )

        self.before_scan_id = before_exposure_data["Scan#"].dropna()
        self.before_locations = before_exposure_data["Location"].dropna()

        self.after_scan_id = after_exposure_data["Scan#"].dropna()
        self.after_locations = after_exposure_data["Location"].dropna()

    def add_tewl_scan(
        self, scan_id, location=None, arm=None, post_exposure=None, return_visit=None
    ):
        """_summary_

        Args:
            visit_id (_type_): _description_
            return_visit (_type_): _description_
            data (_type_): _description_
        """
        if self.scans is None:
            self.scans = []

        self.scans.append(
            Scan(
                scan_id=scan_id,
                arm=arm,
                location=location,
                post_exposure=post_exposure,
                return_visit=return_visit,
            )
        )
        self.num_scans += 1


class Scan:
    def __init__(
        self,
        scan_id,
        arm=None,
        location=None,
        post_exposure=None,
        return_visit=None,
    ):
        self.scan_id = scan_id
        self.arm = arm
        self.location = location
        self.post_exposure = post_exposure
        self.return_visit = return_visit
