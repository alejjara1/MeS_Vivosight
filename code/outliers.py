import numpy as np


def rout_outlier_detection(data, Q=0.01):
    """
    Detect outliers using the ROUT method.

    Parameters:
        data : array-like — input data values
        Q    : float — False Discovery Rate (default 0.01 = 1%)

    Returns:
        dict with:
            'outliers'      : array of outlier values
            'outlier_mask'  : boolean array (True = outlier)
            'clean_data'    : data with outliers removed
            'outlier_idx'   : indices of outliers

    Example:
        data = [12.1, 11.8, 12.3, 12.0, 45.7, 11.9, 12.2, 0.3, 12.1]

        result = rout_outlier_detection(data, Q=0.01)

        print("Original data:  ", data)
        print("Outliers found: ", result["outliers"])
        print("Outlier indices:", result["outlier_idx"])
        print("Clean data:     ", result["clean_data"])

    """
    data = np.array(data, dtype=float)
    n = len(data)

    def fit_robust(d):
        """Iteratively reweighted least squares for robust mean/std."""
        med = np.median(d)
        mad = np.median(np.abs(d - med))
        robust_std = 1.4826 * mad  # MAD to std conversion
        return med, robust_std

    def compute_p_values(d, center, scale):
        """Two-tailed p-values from robust Gaussian fit."""
        from scipy.stats import norm

        if scale == 0:
            return np.ones(len(d))
        z_scores = np.abs(d - center) / scale
        p_values = 2 * (1 - norm.cdf(z_scores))
        return p_values

    def benjamini_hochberg(p_values, Q):
        """Apply BH correction at FDR = Q."""
        n = len(p_values)
        sorted_idx = np.argsort(p_values)
        sorted_p = p_values[sorted_idx]

        bh_threshold = np.zeros(n)
        for i in range(n):
            bh_threshold[i] = (i + 1) / n * Q

        # Find largest k where p(k) <= (k/n)*Q
        reject = sorted_p <= bh_threshold
        if not np.any(reject):
            return np.zeros(n, dtype=bool)

        max_k = np.max(np.where(reject)[0])
        outlier_mask = np.zeros(n, dtype=bool)
        outlier_mask[sorted_idx[: max_k + 1]] = True
        return outlier_mask

    # Iterative removal: fit → find outliers → refit on clean data
    working_data = data.copy()
    working_idx = np.arange(n)
    final_outlier_mask = np.zeros(n, dtype=bool)

    for _ in range(n):  # max iterations = n
        center, scale = fit_robust(working_data)
        p_values = compute_p_values(working_data, center, scale)
        outlier_mask = benjamini_hochberg(p_values, Q)

        if not np.any(outlier_mask):
            break  # No more outliers found

        # Mark outliers in the original index space
        final_outlier_mask[working_idx[outlier_mask]] = True

        # Remove outliers and refit
        keep = ~outlier_mask
        working_data = working_data[keep]
        working_idx = working_idx[keep]

    return {
        "outliers": data[final_outlier_mask],
        "outlier_mask": final_outlier_mask,
        "clean_data": data[~final_outlier_mask],
        "outlier_idx": np.where(final_outlier_mask)[0],
    }


def iqr_outlier_detection(data, multiplier=1.5):
    """
    Detect outliers using the IQR (Interquartile Range) method.

    Parameters:
        data       : array-like — input data values
        multiplier : float — IQR multiplier (default 1.5; use 3.0 for extreme outliers only)

    Returns:
        dict with:
            'outliers'      : array of outlier values
            'outlier_mask'  : boolean array (True = outlier)
            'clean_data'    : data with outliers removed
            'outlier_idx'   : indices of outliers
            'bounds'        : (lower_bound, upper_bound) thresholds used

    Example:
        data = [12.1, 11.8, 12.3, 12.0, 45.7, 11.9, 12.2, 0.3, 12.1]

        result = rout_outlier_detection(data, Q=0.01)

        print("Original data:  ", data)
        print("Outliers found: ", result["outliers"])
        print("Outlier indices:", result["outlier_idx"])
        print("Clean data:     ", result["clean_data"])


    """
    data = np.array(data, dtype=float)

    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR

    outlier_mask = (data < lower_bound) | (data > upper_bound)

    return {
        "outliers": data[outlier_mask],
        "outlier_mask": outlier_mask,
        "clean_data": data[~outlier_mask],
        "outlier_idx": np.where(outlier_mask)[0],
        "bounds": (lower_bound, upper_bound),
    }


def _clean_values(values, method=None, Q=0.01, multiplier=1.5):
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]

    if arr.size == 0 or method is None:
        return arr.tolist()

    if method == "rout":
        return rout_outlier_detection(arr, Q=Q)["clean_data"].tolist()

    if method == "iqr":
        return iqr_outlier_detection(arr, multiplier=multiplier)["clean_data"].tolist()

    raise ValueError(f"Unknown outlier method: {method}")


def _clean_location_data(data_by_location, method=None, Q=0.01, multiplier=1.5):
    cleaned = {}
    for loc, phase_dict in data_by_location.items():
        cleaned[loc] = {
            "pre": _clean_values(
                phase_dict.get("pre", []), method=method, Q=Q, multiplier=multiplier
            ),
            "post": _clean_values(
                phase_dict.get("post", []), method=method, Q=Q, multiplier=multiplier
            ),
        }
    return cleaned


def _clean_exposure_data(data_by_exposure, method=None, Q=0.01, multiplier=1.5):
    cleaned = {}
    for exposure, phase_dict in data_by_exposure.items():
        cleaned[exposure] = {"pre": {}, "post": {}}
        for phase in ("pre", "post"):
            for loc, vals in phase_dict.get(phase, {}).items():
                cleaned[exposure][phase][loc] = _clean_values(
                    vals, method=method, Q=Q, multiplier=multiplier
                )
    return cleaned
