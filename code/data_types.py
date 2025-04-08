import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt

class Subject:
    def __init__(self, subject_id):
        self.subject_id = subject_id
        self.scans = None
        self.skin_roughness = None
        self.epidermal = None
        self.blood_flow = None
        self.num_scans = 0
        self.num_skin_roughness = 0
        self.num_epidermal = 0
        self.num_blood_flow = 0
        self.before_scan_id = None
        self.before_location = None
        self.after_scan_id = None
        self.after_location = None

    def add_skin_roughness(self, skin_roughness_data):
        """
        skin roughness function
        """
        if self.skin_roughness is None:
            self.skin_roughness = []

        self.skin_roughness.append(skin_roughness_data)

        self.num_skin_roughness += 1

    def add_epidermal(self, epidermal_data):
        """
        epidermal data function
        """
        if self.epidermal is None:
            self.epidermal = []

        self.epidermal.append(epidermal_data)

        self.num_epidermal += 1

    def add_blood_flow(self, blood_flow_data):
        """
        blood flow data function
        """
        if self.blood_flow is None:
            self.blood_flow = []

        self.blood_flow.append(blood_flow_data)

        self.num_blood_flow += 1

    def add_scan_data(self, before_exposure_data, after_exposure_data):
        """
        To add...
        """

        self.before_scan_id = before_exposure_data["Scan#"].dropna()
        self.before_location = before_exposure_data["Location"].dropna()

        self.after_scan_id = after_exposure_data["Scan#"].dropna()
        self.after_location = after_exposure_data["Location"].dropna()

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


class Epidermal:
    def __init__(self, data_file, scan_id, location, return_visit):
        self.data_file = data_file
        self.depth_data = pd.read_csv(data_file, header=6, encoding="latin1")
        self.summary_data = pd.read_csv(data_file, header=0, nrows=5, encoding="latin1")
        self.scan_id = scan_id
        self.location = location
        self.return_visit = return_visit
        self.min_value = None
        self.max_value = None

    def find_min_max(self):
        """
        Find the minimum and maximum of the Mean A-scan data
        """
        self.min_value = self.depth_data["Mean A-scan"].min()
        self.max_value = self.depth_data["Mean A-scan"].max()

    def normalize_a_scan(self):
        """
        Normalize the Mean A-scan
        """
        self.find_min_max()
        self.depth_at_max_intensity = self.depth_data["Depth"][
            self.depth_data["Mean A-scan"].idxmax()
        ]
        self.normalized_ascan = (self.depth_data["Mean A-scan"] - self.min_value) / (
            self.max_value - self.min_value
        )

    def get_sid(self):
        """
        Calculate the Standard.....
        """
        value = 0.2
        index = abs(self.normalized_ascan - value).idxmin()
        attenuation_depth = self.depth_data["Depth"].iloc[index]
        self.sid = 0.8 / attenuation_depth

    def get_AuC(self):
        """
        Integrate the curve
        """
        integration_depth = 0.2
        lower_bound_index = self.depth_data["Mean A-scan"].idxmax()
        
        upper_bound_index = abs(
            self.depth_data["Depth"] - (self.depth_at_max_intensity + integration_depth)
        ).idxmin()

        self.AuC = sp.integrate.trapezoid(
            self.normalized_ascan[lower_bound_index:upper_bound_index],
            self.depth_data["Depth"][lower_bound_index:upper_bound_index],
        )


    def plot_a_scan(self, subject_id,exposed):
        """
        Plot the A-scan data
        """
        fig, ax = plt.subplots()         
        plt.plot(self.depth_data["Depth"], self.depth_data["Mean A-scan"], label="Mean A-Scan")
        plt.xticks(visible=False)
        if exposed:
            plt.title(f'Subject id: {subject_id}  Scan id: {self.scan_id} Post-Exposure')
        else:
            plt.title(f'Subject id: {subject_id}  Scan id: {self.scan_id} Pre-Exposure')
        plt.ylim(bottom=0)
        plt.ylabel("Intensity")
        plt.xlabel("Depth (mm)")
        plt.xlim(0,2)
        plt.legend() 
        # plt.savefig(f"../data_out/epidermal_data_out/subject_id_{subject_id}_scan_id_{self.scan_id}.pdf")
        # plt.close()
        plt.show()


class SkinRoughness:
    def __init__(self, data_file, scan_id, location, return_visit):
        self.data_file = data_file

        _roughness_data = pd.read_csv(data_file, header=None, encoding="latin1")
        self.Ra = _roughness_data.iloc[0, 1]
        self.Rz = _roughness_data.iloc[1, 1]
        self.Rq = _roughness_data.iloc[2, 1]

        self.scan_id = scan_id
        self.location = location
        self.return_visit = return_visit


class BloodFlow:
    def __init__(self, data_file, scan_id, location, return_visit):
        self.data_file = data_file
        self.bloodflow_depth_data = pd.read_csv(data_file, header=1, encoding="latin1")
        _plexus_data = pd.read_csv(data_file, header=0, nrows=0, encoding="latin1")
        self.plexus_data = float(_plexus_data.columns[1].split(" ")[0])
        self.scan_id = scan_id
        self.location = location
        self.return_visit = return_visit
