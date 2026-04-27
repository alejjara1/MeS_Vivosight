import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import AutoMinorLocator
from all_subjects_data_collector import DataFactory, compute_wilcoxon_stats


def _draw_top_marker(
    ax, x_pos, label, line_y, line_half_width, hook_height, fontsize=12
):
    ax.plot(
        [x_pos - line_half_width, x_pos + line_half_width],
        [line_y, line_y],
        color="black",
        linewidth=1,
    )
    ax.plot(
        [x_pos - line_half_width, x_pos - line_half_width],
        [line_y, line_y - hook_height],
        color="black",
        linewidth=1,
    )
    ax.plot(
        [x_pos + line_half_width, x_pos + line_half_width],
        [line_y, line_y - hook_height],
        color="black",
        linewidth=1,
    )
    ax.text(
        x_pos,
        line_y + hook_height * 0.35,
        label,
        ha="center",
        va="bottom",
        fontsize=fontsize,
    )


def plot_data_by_location(depth_data, plot_dir, data_type, data_label, legend=False):
    """
    Plot the epidermal depths by location

    Args:
        depth_data: dict with structure {subject_id: {loc: {"pre": value, "post": value}}}
    """
    plt.figure(figsize=(10, 6))

    count_by_loc = {loc: 0 for loc in [1, 2, 3, 4]}
    all_y_vals = []
    for exposure, subjects in depth_data.items():
        for subject_id, locations in subjects.items():
            for loc in [1, 2, 3, 4]:

                if loc not in locations:
                    continue

                pre_vals = locations[loc].get("pre")
                post_vals = locations[loc].get("post")

                if not pre_vals or not post_vals:
                    continue

                if pre_vals > 0 and post_vals > 0:
                    count_by_loc[loc] += 1
                    all_y_vals.extend([pre_vals, post_vals])

                    x_vals = [loc - 0.1, loc + 0.1]
                    y_vals = [pre_vals, post_vals]

                    # Line
                    plt.plot(x_vals, y_vals, color="gray", alpha=0.5)

                    # Dots
                    plt.scatter(
                        loc - 0.1, pre_vals, color="blue", edgecolor="black", zorder=3
                    )
                    plt.scatter(
                        loc + 0.1, post_vals, color="red", edgecolor="black", zorder=3
                    )

    max_y = max(all_y_vals) if all_y_vals else 0.05
    min_y = min(all_y_vals) if all_y_vals else 0.0
    y_range = max_y - min_y
    marker_y = max_y + y_range * 0.06
    label_y = marker_y + y_range * 0.05

    ax = plt.gca()
    for loc in [1, 2, 3, 4]:
        _draw_top_marker(
            ax,
            loc,
            f"N={count_by_loc[loc]}",
            marker_y,
            line_half_width=0.12,
            hook_height=y_range * 0.012,
            fontsize=11,
        )

    # Legend
    if legend:
        blue_patch = mpatches.Patch(color="blue", label="Pre-Exposure")
        red_patch = mpatches.Patch(color="red", label="Post-Exposure")
        plt.legend(
            handles=[blue_patch, red_patch],
            loc="lower center",
            ncol=2,
            fontsize=12,
            bbox_to_anchor=(0.5, -0.18),
            frameon=True,
        )

    # Labeling
    plt.xticks([1, 2, 3, 4], [f"{i}" for i in range(1, 5)], fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel("Scan Location", fontsize=14)
    plt.ylabel(data_label, fontsize=14)
    plt.ylim(min_y - y_range * 0.05, label_y + y_range * 0.08)
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.7)
    ax.grid(True, which="minor", axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(plot_dir + data_type + "_vs_location.pdf")


def plot_data_by_location_exposure(
    depth_data_by_exposure,
    plot_dir,
    data_type,
    data_label,
    label_points=False,
    legend=False,
):
    """
    Plot epidermal depths by location and exposure level

    Args:
        depth_data_by_exposure: dict with structure {exposure: {subject_id: {loc: {"pre": value, "post": value}}}}
        label_points: bool, whether to label points with subject IDs
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    count_by_exposure = {
        exposure: {loc: 0 for loc in [1, 2, 3, 4]}
        for exposure in ["Low", "Med", "High"]
    }
    all_y_vals = []

    # Map exposure levels to subplot indices
    exposure_map = {"Low": 0, "Med": 1, "High": 2}

    for exposure, subjects in depth_data_by_exposure.items():
        ax_idx = exposure_map[exposure]

        for subject_id, locations in subjects.items():
            for loc in [1, 2, 3, 4]:
                if loc not in locations:
                    continue

                pre_vals = locations[loc].get("pre")
                post_vals = locations[loc].get("post")

                if not pre_vals or not post_vals:
                    continue

                if pre_vals > 0 and post_vals > 0:
                    count_by_exposure[exposure][loc] += 1
                    all_y_vals.extend([pre_vals, post_vals])

                    x_vals = [loc - 0.1, loc + 0.1]
                    y_vals = [pre_vals, post_vals]

                    # Line
                    axes[ax_idx].plot(x_vals, y_vals, color="gray", alpha=0.5)

                    # Dots
                    axes[ax_idx].scatter(
                        loc - 0.1,
                        pre_vals,
                        color="blue",
                        edgecolor="black",
                        zorder=3,
                    )
                    axes[ax_idx].scatter(
                        loc + 0.1, post_vals, color="red", edgecolor="black", zorder=3
                    )

                    if label_points:
                        axes[ax_idx].text(
                            loc - 0.1,
                            pre_vals,
                            subject_id,
                            fontsize=8,
                            ha="center",
                            va="bottom",
                        )
                        axes[ax_idx].text(
                            loc + 0.1,
                            post_vals,
                            subject_id,
                            fontsize=8,
                            ha="center",
                            va="bottom",
                        )

    max_y = max(all_y_vals) if all_y_vals else 0.05
    min_y = min(all_y_vals) if all_y_vals else 0.0
    y_range = max_y - min_y
    marker_y = max_y + y_range * 0.06
    label_y = marker_y + y_range * 0.05

    # Style each subplot
    for idx, (exposure_name, ax) in enumerate(
        [("Low", axes[0]), ("Med", axes[1]), ("High", axes[2])]
    ):
        for loc in [1, 2, 3, 4]:
            _draw_top_marker(
                ax,
                loc,
                f"N={count_by_exposure[exposure_name][loc]}",
                marker_y,
                line_half_width=0.12,
                hook_height=y_range * 0.012,
                fontsize=11,
            )

        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.7)
        ax.grid(True, which="minor", axis="y", linestyle="--", alpha=0.35)

        ax.set_xticks([1, 2, 3, 4])
        ax.set_xticklabels([f"{i}" for i in range(1, 5)], fontsize=12)
        ax.tick_params(axis="y", labelsize=12)
        ax.set_xlabel("Scan Location", fontsize=14)
        ax.set_ylim(min_y - y_range * 0.05, label_y + y_range * 0.08)
        # ax.set_ylim(0, None)
        if idx == 0:
            ax.set_ylabel(data_label, fontsize=14)
        ax.set_title(f"Exposure: {exposure_name}", fontsize=14)

    # Single legend at bottom
    if legend:
        blue_patch = mpatches.Patch(color="blue", label="Pre-Exposure")
        red_patch = mpatches.Patch(color="red", label="Post-Exposure")
        fig.legend(
            handles=[blue_patch, red_patch],
            loc="lower center",
            ncol=2,
            fontsize=12,
            bbox_to_anchor=(0.525, 0.125),
            frameon=True,
        )

    plt.tight_layout()
    plt.savefig(
        plot_dir + data_type + "_vs_location_by_exposure.pdf", bbox_inches="tight"
    )


def plot_box_by_location(
    combined_depth_data_by_location,
    stats_by_loc,
    data_type,
    y_label,
    plot_dir,
    combine_locations_1_2=False,
):
    """
    Box and whisker plot of epidermal depths differences by location.
    """
    diff_by_loc = {
        loc: combined_depth_data_by_location[loc]["diff"]
        for loc in DataFactory.LOCATIONS
    }

    locations_to_plot = [1, 2, 3, 4]
    location_labels = ["1", "2", "3", "4"]
    if combine_locations_1_2:
        diff_by_loc["1+2"] = combined_depth_data_by_location["1+2"]["diff"]
        locations_to_plot.insert(2, "1+2")
        location_labels.insert(2, "1+2")

    plot_data = []
    positions = []
    box_colors = []
    for pos, loc in enumerate(locations_to_plot, start=1):
        plot_data.extend([diff_by_loc[loc]])
        positions.extend([pos])
        if loc in [1, 2]:
            box_colors.append("lightblue")
        elif loc in ["1+2"]:
            box_colors.append("steelblue")
        else:
            box_colors.append("bisque")

    plt.figure(figsize=(10, 6))
    bp = plt.boxplot(
        plot_data,
        positions=positions,
        widths=0.3,
        showfliers=True,
        patch_artist=True,
        medianprops=dict(color="black", linewidth=1.5),
        boxprops=dict(facecolor="None"),
    )

    for box, color in zip(bp["boxes"], box_colors):
        box.set_facecolor(color)

    # Find min/max y for consistent star placement
    all_vals = []
    for loc in locations_to_plot:
        all_vals.extend(diff_by_loc[loc])
    max_y = max(all_vals) if all_vals else 0.05
    min_y = min(all_vals) if all_vals else 0.0
    y_range = max_y - min_y
    y_scale = y_range if y_range > 0 else max(abs(max_y), 1.0)
    marker_y = max_y + y_scale * 0.06
    star_y = marker_y + y_scale * 0.05

    plot_stats_by_loc = dict(stats_by_loc)
    if combine_locations_1_2:
        assert "1+2" in plot_stats_by_loc

    # Add significance stars
    pos_by_loc = {loc: pos for pos, loc in enumerate(locations_to_plot, start=1)}
    for loc in locations_to_plot:
        if loc not in plot_stats_by_loc:
            continue
        star = plot_stats_by_loc[loc]["star"]
        _draw_top_marker(
            plt.gca(),
            pos_by_loc[loc],
            star,
            marker_y,
            line_half_width=0.12,
            hook_height=y_scale * 0.012,
        )

    plt.xlabel("Scan Location", fontsize=14)
    plt.ylabel(f"$\Delta$ {y_label}", fontsize=14)
    plt.xticks(positions, location_labels, fontsize=12)
    plt.ylim(min_y - y_scale * 0.15, star_y + y_scale * 0.08)

    ax = plt.gca()
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.7)
    ax.grid(True, which="minor", axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(plot_dir + f"boxplot_by_location_{data_type}.pdf")


def plot_box_by_location_exposure(
    exposure_data_dict,
    exposure_stats_dict,
    data_type,
    y_label,
    plot_dir,
    combine_locations_1_2=False,
):
    """
    Box and whisker plot of differences by location and exposure.
    """
    exposure_groups = ["Low", "Med", "High"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)

    # Calculate global max for consistent y-axis
    all_exposure_vals = []
    for exposure in exposure_groups:
        diff_by_loc = exposure_data_dict[exposure]["diff"]
        for loc in [1, 2, 3, 4]:
            all_exposure_vals.extend(diff_by_loc[loc])

    max_y_all = max(all_exposure_vals) if all_exposure_vals else 0.05
    min_y_all = min(all_exposure_vals) if all_exposure_vals else 0.00
    y_range_all = max_y_all - min_y_all
    y_scale_all = y_range_all if y_range_all > 0 else max(abs(max_y_all), 1.0)

    # Plot with consistent y limits
    for idx, exposure in enumerate(exposure_groups):
        diff_by_loc = exposure_data_dict[exposure]["diff"]
        stats_by_loc = dict(exposure_stats_dict[exposure])

        locations_to_plot = [1, 2, 3, 4]
        location_labels = ["1", "2", "3", "4"]
        if combine_locations_1_2:
            locations_to_plot.insert(2, "1+2")
            location_labels.insert(2, "1+2")
            assert "1+2" in stats_by_loc

        plot_data = []
        positions = []
        box_colors = []
        for pos, loc in enumerate(locations_to_plot, start=1):
            plot_data.extend([diff_by_loc[loc]])
            positions.extend([pos])
            if loc in [1, 2]:
                box_colors.append("lightblue")
            elif loc in ["1+2"]:
                box_colors.append("steelblue")
            else:
                box_colors.append("bisque")

        bp = axes[idx].boxplot(
            plot_data,
            positions=positions,
            widths=0.3,
            showfliers=True,
            patch_artist=True,
            medianprops=dict(color="black", linewidth=1.5),
            boxprops=dict(facecolor="None"),
        )

        for box, color in zip(bp["boxes"], box_colors):
            box.set_facecolor(color)

        # Use global max y for consistent star placement across all exposures
        marker_y_exp = max_y_all + y_scale_all * 0.06
        star_y_exp = marker_y_exp + y_scale_all * 0.05

        # Add significance stars
        pos_by_loc = {loc: pos for pos, loc in enumerate(locations_to_plot, start=1)}
        for loc in locations_to_plot:
            if loc not in stats_by_loc:
                continue
            star = stats_by_loc[loc]["star"]
            _draw_top_marker(
                axes[idx],
                pos_by_loc[loc],
                star,
                marker_y_exp,
                line_half_width=0.12,
                hook_height=y_scale_all * 0.012,
            )

        axes[idx].set_title(f"Exposure: {exposure}", fontsize=14)
        axes[idx].set_xlabel("Scan Location", fontsize=14)
        axes[idx].set_xticks(positions)
        axes[idx].set_xticklabels(location_labels, fontsize=12)
        axes[idx].tick_params(axis="y", labelsize=12)
        axes[idx].yaxis.set_minor_locator(AutoMinorLocator(2))
        axes[idx].grid(True, which="major", axis="y", linestyle="--", alpha=0.7)
        axes[idx].grid(True, which="minor", axis="y", linestyle="--", alpha=0.35)
        axes[idx].set_ylim(
            min_y_all - y_scale_all * 0.15, star_y_exp + y_scale_all * 0.08
        )
        if idx == 0:
            axes[idx].set_ylabel(f"$\Delta$ {y_label}", fontsize=14)

    plt.tight_layout()
    plt.savefig(
        plot_dir + f"boxplot_by_location_exposure_{data_type}.pdf",
        bbox_inches="tight",
    )


def plot_scatter_by_exposure(
    x_data_by_exposure,
    y_data_by_exposure,
    x_label,
    y_label,
    output_path,
    xlim=None,
    ylim=None,
):
    """
    Plot scatter with regression by exposure group (subplots), with R² per exposure.
    Pre and post points are colored differently and regression uses combined data.

    Args:
        x_data_by_exposure: dict with structure {exposure: {"pre": [x values], "post": [x values]}}
        y_data_by_exposure: dict with structure {exposure: {"pre": [y values], "post": [y values]}}
        x_label: label for x-axis
        y_label: label for y-axis
        output_path: file path to save plot
        xlim: tuple or None, optional x-axis limits
        ylim: tuple or None, optional y-axis limits
    """
    from scipy.stats import linregress

    exposure_colors = {"Low": "blue", "Med": "green", "High": "red"}
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for idx, exposure in enumerate(["Low", "Med", "High"]):
        color = exposure_colors[exposure]

        # Pre and post data
        x_pre = x_data_by_exposure[exposure]["pre"]
        y_pre = y_data_by_exposure[exposure]["pre"]
        x_post = x_data_by_exposure[exposure]["post"]
        y_post = y_data_by_exposure[exposure]["post"]

        # Plot pre points (lighter/open markers)
        axes[idx].scatter(
            x_pre,
            y_pre,
            color="black",
            s=50,
            alpha=0.4,
            edgecolor="black",
            marker="o",
            label="Pre",
        )

        # Plot post points (darker/filled markers)
        axes[idx].scatter(
            x_post,
            y_post,
            color=color,
            s=100,
            alpha=0.7,
            edgecolor="black",
            marker="s",
            label="Post",
        )

        # Separate regression for pre and post data
        r_squared_pre = None
        r_squared_post = None

        if len(x_pre) > 1:
            slope_pre, intercept_pre, r_value_pre, _, _ = linregress(x_pre, y_pre)
            r_squared_pre = r_value_pre**2

            x_line_pre = np.array([min(x_pre), max(x_pre)])
            y_line_pre = slope_pre * x_line_pre + intercept_pre
            axes[idx].plot(
                x_line_pre,
                y_line_pre,
                color="black",
                linewidth=2,
                alpha=0.4,
                linestyle="--",
                label="Pre fit",
            )

        if len(x_post) > 1:
            slope_post, intercept_post, r_value_post, _, _ = linregress(x_post, y_post)
            r_squared_post = r_value_post**2

            x_line_post = np.array([min(x_post), max(x_post)])
            y_line_post = slope_post * x_line_post + intercept_post
            axes[idx].plot(
                x_line_post,
                y_line_post,
                color=color,
                linewidth=2,
                alpha=0.7,
                label="Post fit",
            )

        # Display both R² values
        text_str = ""
        if r_squared_pre is not None:
            text_str += f"R²(pre) = {r_squared_pre:.3f}\n"
        if r_squared_post is not None:
            text_str += f"R²(post) = {r_squared_post:.3f}"

        if text_str:
            axes[idx].text(
                0.70,
                0.98,
                text_str,
                transform=axes[idx].transAxes,
                fontsize=10,
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="white",
                    edgecolor="black",
                    alpha=0.8,
                ),
                verticalalignment="top",
            )

        axes[idx].set_xlabel(x_label, fontsize=12)
        axes[idx].set_title(f"Exposure: {exposure}", fontsize=13)
        axes[idx].yaxis.set_minor_locator(AutoMinorLocator(2))
        axes[idx].xaxis.set_minor_locator(AutoMinorLocator(2))
        axes[idx].grid(True, which="major", linestyle="--", alpha=0.7)
        axes[idx].grid(True, which="minor", linestyle="--", alpha=0.35)
        if xlim is not None:
            axes[idx].set_xlim(*xlim)
        if ylim is not None:
            axes[idx].set_ylim(*ylim)
        if idx == 0:
            axes[idx].set_ylabel(y_label, fontsize=12)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_tewl_subject_averages_by_location(subject_data, output_path):
    """Plot scan-level TEWL averages for all subjects by location.

    Marker shape indicates visit type:
    - Initial visit: circle
    - Return visit: triangle
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    colors_by_loc = {1: "#1f77b4", 2: "#2ca02c", 3: "#ff7f0e", 4: "#d62728"}
    marker_by_visit = {False: "o", True: "^"}

    # Small deterministic jitter to reduce overlap at each location.
    rng = np.random.default_rng(42)

    plotted_visit_type = {False: False, True: False}

    for subject in subject_data.values():
        for scan in subject.scans:
            if scan.location not in [1, 2, 3]:
                continue

            tewl_values = scan.data.get("TM_TEWL")
            if tewl_values is None:
                continue

            avg_val = np.mean(tewl_values)
            if not np.isfinite(avg_val):
                continue

            jitter = rng.uniform(-0.08, 0.08)
            x_val = scan.location + jitter

            visit_type = bool(scan.return_visit)
            label = None
            if not plotted_visit_type[visit_type]:
                label = "Return Visit" if visit_type else "Initial Visit"
                plotted_visit_type[visit_type] = True

            ax.scatter(
                x_val,
                avg_val,
                s=70,
                marker=marker_by_visit[visit_type],
                color=colors_by_loc[scan.location],
                edgecolor="black",
                alpha=0.85,
                label=label,
            )

    ax.set_xticks([1, 2, 3])
    ax.set_xlabel("Scan Location", fontsize=14)
    ax.set_ylabel("Average TEWL (g/m$^2$-h)", fontsize=14)
    ax.set_title("Average TEWL by Location (All Subjects)", fontsize=16)
    ax.tick_params(axis="both", labelsize=12)
    ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.7)

    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_subject_diff_vs_tewl(
    subject_diff,
    tewl_average,
    output_path,
    x_label="Average TEWL (Location 1)",
    y_label="Average Epidermal Diff",
):
    """Plot subject-level epidermal diff against TEWL averages.

    Args:
        subject_diff: dict {subject_id: diff_value}
        tewl_average: dict {subject_id: tewl_value}
        output_path: file path to save plot
        x_label: x-axis label
        y_label: y-axis label
    """
    x_vals = []
    y_vals = []

    for subject_id, diff_val in subject_diff.items():
        tewl_val = tewl_average.get(subject_id)
        if diff_val is None or tewl_val is None:
            continue
        if not (np.isfinite(diff_val) and np.isfinite(tewl_val)):
            continue

        x_vals.append(float(tewl_val))
        y_vals.append(float(diff_val))

    fig, ax = plt.subplots(figsize=(7, 5))
    r_squared = None

    if x_vals:
        ax.scatter(
            x_vals,
            y_vals,
            s=70,
            alpha=0.85,
            color="#1f77b4",
            edgecolor="black",
        )

        if len(x_vals) > 1:
            slope, intercept = np.polyfit(x_vals, y_vals, 1)
            x_line = np.array([min(x_vals), max(x_vals)])
            y_line = slope * x_line + intercept
            ax.plot(x_line, y_line, color="black", linewidth=2, alpha=0.8)

            y_pred = slope * np.array(x_vals) + intercept
            ss_res = np.sum((np.array(y_vals) - y_pred) ** 2)
            ss_tot = np.sum((np.array(y_vals) - np.mean(y_vals)) ** 2)
            if ss_tot > 0:
                r_squared = 1 - (ss_res / ss_tot)

    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title("TEWL vs Epidermal Difference", fontsize=13)
    ax.grid(True, which="major", linestyle="--", alpha=0.7)
    if r_squared is not None:
        ax.text(
            0.02,
            0.98,
            f"$R^2$ = {r_squared:.3f}",
            transform=ax.transAxes,
            va="top",
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
        )

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_subject_diff_heatmap(
    subject_diff_by_parameter,
    output_path,
    title="Subject-Level Epidermal Difference Heatmap",
):
    """Plot one heatmap of subject-level diffs across all parameters.

    Args:
        subject_diff_by_parameter: dict {parameter: {subject_id: diff_value}}
        output_path: file path to save plot
        title: plot title
    """
    if not subject_diff_by_parameter:
        return

    parameters = list(subject_diff_by_parameter.keys())
    subject_ids = sorted(
        {
            subject_id
            for param_data in subject_diff_by_parameter.values()
            for subject_id in param_data.keys()
        }
    )

    if not subject_ids:
        return

    matrix = np.full((len(subject_ids), len(parameters)), np.nan, dtype=float)

    for col_idx, parameter in enumerate(parameters):
        param_data = subject_diff_by_parameter[parameter]
        for row_idx, subject_id in enumerate(subject_ids):
            value = param_data.get(subject_id)
            if value is None or not np.isfinite(value):
                continue
            matrix[row_idx, col_idx] = float(value)

    finite_vals = matrix[np.isfinite(matrix)]
    if finite_vals.size == 0:
        return

    # Normalize each parameter independently so columns with different scales
    # are directly comparable in one heatmap.
    normalized_matrix = np.full_like(matrix, np.nan, dtype=float)
    for col_idx in range(matrix.shape[1]):
        col_vals = matrix[:, col_idx]
        finite_mask = np.isfinite(col_vals)
        if not np.any(finite_mask):
            continue

        mean_val = np.mean(col_vals[finite_mask])
        std_val = np.std(col_vals[finite_mask])

        if std_val > 0:
            normalized_matrix[finite_mask, col_idx] = (
                col_vals[finite_mask] - mean_val
            ) / std_val
        else:
            # Constant column -> normalized variation is zero.
            normalized_matrix[finite_mask, col_idx] = 0.0

    normalized_finite_vals = normalized_matrix[np.isfinite(normalized_matrix)]
    if normalized_finite_vals.size == 0:
        return

    max_abs = np.max(np.abs(normalized_finite_vals))
    if max_abs == 0:
        max_abs = 1.0

    cmap = matplotlib.colormaps["RdBu_r"].copy()
    cmap.set_bad(color="#d9d9d9")

    fig_width = max(7, 1.6 * len(parameters) + 2)
    fig_height = max(6, 0.3 * len(subject_ids) + 2)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    ax.imshow(
        normalized_matrix,
        cmap=cmap,
        aspect="auto",
        vmin=-max_abs,
        vmax=max_abs,
        interpolation="nearest",
    )

    # Annotate each cell with the raw (un-normalized) value.
    font_size = 8
    for row_idx in range(len(subject_ids)):
        for col_idx in range(len(parameters)):
            raw = matrix[row_idx, col_idx]
            if not np.isfinite(raw):
                ax.text(
                    col_idx,
                    row_idx,
                    "NA",
                    ha="center",
                    va="center",
                    fontsize=font_size,
                    color="black",
                )
                continue
            norm_val = normalized_matrix[row_idx, col_idx]
            text_color = "white" if abs(norm_val) > max_abs * 0.6 else "black"
            ax.text(
                col_idx,
                row_idx,
                f"{norm_val:.2f}",
                ha="center",
                va="center",
                fontsize=font_size,
                color=text_color,
            )

    ax.set_xticks(range(len(parameters)))
    wrapped_params = [p.replace("_", "\n") for p in parameters]
    ax.set_xticklabels(
        wrapped_params,
        rotation=35,
        ha="right",
        rotation_mode="anchor",
        fontsize=9,
    )
    ax.tick_params(axis="x", which="major", pad=8)
    ax.set_yticks(range(len(subject_ids)))
    ax.set_yticklabels(subject_ids, fontsize=8)
    ax.set_xlabel("Parameter", fontsize=12)
    ax.set_ylabel("Subject ID", fontsize=12)
    ax.set_title(f"{title} (z-score normalized)", fontsize=13)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
