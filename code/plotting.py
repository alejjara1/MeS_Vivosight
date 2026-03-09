import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import AutoMinorLocator
from all_subjects_data_collector import DataFactory


def plot_depth_by_location(depth_data, plot_dir, legend=False):
    """
    Plot the epidermal depths by location

    Args:
        depth_data: dict with structure {subject_id: {loc: {"pre": value, "post": value}}}
    """
    plt.figure(figsize=(10, 6))
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
    plt.ylabel("Epidermal Thickness ($\mu$m)", fontsize=14)
    # plt.ylim(0, None)
    # plt.title("Inflection Depths by Location")
    ax = plt.gca()
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.7)
    ax.grid(True, which="minor", axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(plot_dir + "epidermis_vs_location.pdf")


def plot_depth_by_location_exposure(
    depth_data_by_exposure, plot_dir, label_points=False, legend=False
):
    """
    Plot epidermal depths by location and exposure level

    Args:
        depth_data_by_exposure: dict with structure {exposure: {subject_id: {loc: {"pre": value, "post": value}}}}
        label_points: bool, whether to label points with subject IDs
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

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

    # Style each subplot
    for idx, (exposure_name, ax) in enumerate(
        [("Low", axes[0]), ("Med", axes[1]), ("High", axes[2])]
    ):
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.7)
        ax.grid(True, which="minor", axis="y", linestyle="--", alpha=0.35)

        ax.set_xticks([1, 2, 3, 4])
        ax.set_xticklabels([f"{i}" for i in range(1, 5)], fontsize=12)
        ax.tick_params(axis="y", labelsize=12)
        ax.set_xlabel("Scan Location", fontsize=14)
        # ax.set_ylim(0, None)
        if idx == 0:
            ax.set_ylabel("Epidermal Thickness ($\mu$m)", fontsize=14)
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
    plt.savefig(plot_dir + "depth_vs_location_by_exposure.pdf", bbox_inches="tight")


def plot_box_by_location(
    combined_depth_data_by_location,
    stats_by_loc,
    data_type,
    y_label,
    plot_dir,
    legend=False,
):
    """
    Box and whisker plot of epidermal depths by location with separate pre/post boxes.

    Args:
        combined_depth_data_by_location: dict with structure {loc: {"pre": [values], "post": [values]}}
        stats_by_loc: dict with structure {loc: {"p_val": float, "star": str}}
    """
    pre_by_loc = {
        loc: combined_depth_data_by_location[loc]["pre"]
        for loc in DataFactory.LOCATIONS
    }
    post_by_loc = {
        loc: combined_depth_data_by_location[loc]["post"]
        for loc in DataFactory.LOCATIONS
    }

    plot_data = []
    positions = []
    colors = []
    for loc in [1, 2, 3, 4]:
        plot_data.extend([pre_by_loc[loc], post_by_loc[loc]])
        positions.extend([loc - 0.2, loc + 0.2])
        colors.extend(["blue", "red"])

    plt.figure(figsize=(10, 6))
    bp = plt.boxplot(
        plot_data,
        positions=positions,
        widths=0.3,
        showfliers=True,
        patch_artist=True,
        medianprops=dict(color="black", linewidth=1.5),
    )
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)

    # Find min/max y for consistent star placement
    all_vals = []
    for loc in [1, 2, 3, 4]:
        all_vals.extend(pre_by_loc[loc] + post_by_loc[loc])
    max_y = max(all_vals) if all_vals else 0.05
    min_y = min(all_vals) if all_vals else 0.0
    star_y = max_y * 1.08

    # Add significance stars for pre vs post per location
    for loc in [1, 2, 3, 4]:
        if loc not in stats_by_loc:
            continue
        star = stats_by_loc[loc]["star"]
        plt.plot([loc - 0.2, loc + 0.2], [star_y, star_y], color="black", linewidth=1)
        plt.text(loc, star_y, star, ha="center", va="bottom", fontsize=12)
    plt.xlabel("Scan Location", fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    plt.xticks([1, 2, 3, 4], ["1", "2", "3", "4"], fontsize=12)
    plt.ylim(min_y * 0.85, max_y * 1.15)

    if legend:
        blue_patch = mpatches.Patch(color="blue", label="Pre-Exposure")
        red_patch = mpatches.Patch(color="red", label="Post-Exposure")
        plt.legend(
            handles=[blue_patch, red_patch],
            loc="lower center",
            ncol=2,
            fontsize=12,
            bbox_to_anchor=(0.5, 0.0),
            frameon=True,
        )

    ax = plt.gca()
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.7)
    ax.grid(True, which="minor", axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(plot_dir + f"{data_type}_boxplot_by_location.pdf")


def plot_box_by_location_exposure(
    exposure_data_dict, exposure_stats_dict, data_type, y_label, plot_dir, legend=False
):
    """
    Box and whisker plot of epidermal depths by location and exposure
    with separate pre/post boxes.

    Args:
        exposure_data_dict: dict with structure {exposure: {"pre": {loc: [values]}, "post": {loc: [values]}}}
        exposure_stats_dict: dict with structure {exposure: {loc: {"p_val": float, "star": str}}}
    """
    exposure_groups = ["Low", "Med", "High"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)

    # Calculate global max for consistent y-axis
    all_exposure_vals = []
    for exposure in exposure_groups:
        pre_by_loc = exposure_data_dict[exposure]["pre"]
        post_by_loc = exposure_data_dict[exposure]["post"]
        for loc in [1, 2, 3, 4]:
            all_exposure_vals.extend(pre_by_loc[loc] + post_by_loc[loc])

    max_y_all = max(all_exposure_vals) if all_exposure_vals else 0.05
    min_y_all = min(all_exposure_vals) if all_exposure_vals else 0.00

    # Plot with consistent y limits
    for idx, exposure in enumerate(exposure_groups):
        pre_by_loc = exposure_data_dict[exposure]["pre"]
        post_by_loc = exposure_data_dict[exposure]["post"]
        stats_by_loc = exposure_stats_dict[exposure]

        plot_data = []
        positions = []
        colors = []
        for loc in [1, 2, 3, 4]:
            plot_data.extend([pre_by_loc[loc], post_by_loc[loc]])
            positions.extend([loc - 0.2, loc + 0.2])
            colors.extend(["blue", "red"])

        bp = axes[idx].boxplot(
            plot_data,
            positions=positions,
            widths=0.3,
            showfliers=True,
            patch_artist=True,
            medianprops=dict(color="black", linewidth=1.5),
        )
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)

        # Use global max y for consistent star placement across all exposures
        star_y_exp = max_y_all * 1.08

        # Add significance stars for pre vs post per location
        for loc in [1, 2, 3, 4]:
            if loc not in stats_by_loc:
                continue
            star = stats_by_loc[loc]["star"]
            axes[idx].plot(
                [loc - 0.2, loc + 0.2],
                [star_y_exp, star_y_exp],
                color="black",
                linewidth=1,
            )
            axes[idx].text(loc, star_y_exp, star, ha="center", va="bottom", fontsize=8)
        axes[idx].set_title(f"Exposure: {exposure}", fontsize=14)
        axes[idx].set_xlabel("Scan Location", fontsize=14)
        axes[idx].set_xticks([1, 2, 3, 4])
        axes[idx].set_xticklabels(["1", "2", "3", "4"], fontsize=12)
        axes[idx].tick_params(axis="y", labelsize=12)
        axes[idx].yaxis.set_minor_locator(AutoMinorLocator(2))
        axes[idx].grid(True, which="major", axis="y", linestyle="--", alpha=0.7)
        axes[idx].grid(True, which="minor", axis="y", linestyle="--", alpha=0.35)
        axes[idx].set_ylim(min_y_all * 0.85, max_y_all * 1.15)
        if idx == 0:
            axes[idx].set_ylabel(y_label, fontsize=14)

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
        plot_dir + f"{data_type}_boxplot_by_location_exposure.pdf",
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
