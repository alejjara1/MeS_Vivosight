import pandas as pd


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

    def add_scan(
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
