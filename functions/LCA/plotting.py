import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import math
from config import settings

def plot_global_GWP(GWP_df, bins=20):
    sns.set_theme()  # Use seaborn style
    fig, ax = plt.subplots()
    total = GWP_df.loc["GWP", "Total"]  # Extract data to plot
    ax.hist(total, bins=bins)

    # Set title and labels
    ax.set_xlabel(settings.labels.LCA_output_plotting_string)
    ax.set_ylabel("Monte Carlo Iterations")

    # Display plot
    plt.tight_layout()
    plt.show()

    return ax


def plot_average_GWP_byprocess(GWP_df, legend_loc="plot", short_labels=True,
                               save=(False, "placeholder_save_location_str")):
    """


    Notes: Generally legend_loc="plot" and short_labels=True OR legend_loc="box" and short_labels=False produces the
    best results.

    Parameters
    ----------
    GWP_df
    legend_loc: str
        Determine whether subprocess labels should be placed on plot ("plot") or in legend box ("box").
    short_labels: bool
        Determines whether shortened labels should be used (True) or not (False).
    save

    Returns
    -------

    """
    # TODO: Add save functionality to this figure creation function and the other ones too.
    # Setup general variables
    sns.set_theme()
    bar_width = 0.5
    x_array = list(GWP_df.columns)  # Get x-axis for plotting

    # Initialise figure
    fig, ax = plt.subplots()

    # Plotting logic
    for process_count in np.arange(len(GWP_df.columns) - 1):
        # Get arrays of subprocess GWP values and names
        subprocess_names = np.transpose(GWP_df.loc["subprocess_names", GWP_df.columns[process_count]])
        if short_labels:
            subprocess_short_labels = np.transpose(GWP_df.loc["subprocess_abbreviations", GWP_df.columns[process_count]])

        subprocess_GWPs = np.transpose(GWP_df.loc["subprocess_GWP", GWP_df.columns[process_count]])

        # Get subprocess means and labels
        for subprocess_count, _ in enumerate(list(subprocess_GWPs)):
            subprocess_GWP_mean = np.mean(subprocess_GWPs[subprocess_count])  # calculate subprocess GWP mean
            subprocess_label = subprocess_names[subprocess_count][0]  # get subprocess name
            if short_labels:
                subprocess_label = subprocess_short_labels[subprocess_count]  # get shorthand labels for plotting
            y_array = np.zeros(len(x_array))  # Initialise y-array
            y_array[process_count] = subprocess_GWP_mean  # Update y-array with GWP in appropriate position

            # Plot stacked bar graph for individual process
            if subprocess_count == 0:  # plot first subprocess
                ax.bar(x_array, y_array, bar_width, label=subprocess_label)
                if subprocess_GWP_mean > 0:  # positive number case
                    running_total_pos = y_array
                    running_total_neg = np.zeros(len(x_array))  # Initialise other case as zero
                else:  # negative number case
                    running_total_neg = y_array
                    running_total_pos = np.zeros(len(x_array))  # Initialise other case as zero
            else:  # plot other subprocesses
                if subprocess_GWP_mean > 0:  # positive number case
                    ax.bar(x_array, y_array, bar_width, bottom=running_total_pos, label=subprocess_label)
                    running_total_pos += y_array  # update running total
                else:  # negative number case
                    ax.bar(x_array, y_array, bar_width, bottom=running_total_neg, label=subprocess_label)
                    running_total_neg += y_array  # update running total

            # Plot labels on graph
            if legend_loc == "plot":
                if abs(y_array[process_count]) > 50:  # Set threshold for minimum stack size to avoid overlapping labels
                    if subprocess_GWP_mean > 0:
                        y_position = (running_total_pos[process_count] - y_array[process_count]) \
                                     + y_array[process_count] * 0.5
                    else:
                        y_position = (running_total_neg[process_count] - y_array[process_count]) \
                                     + y_array[process_count] * 0.5

                    plt.text(x=x_array[process_count],
                             y=y_position,
                             s=subprocess_label,
                             color="black",
                             fontsize=12,
                             horizontalalignment='center'
                             )

    # Add final bar showing total/overall GWP
    y_array = np.zeros(len(x_array))  # Initialise y-array
    y_array[process_count + 1] = np.mean(GWP_df.loc["GWP", "Total"])  # Update y-array with GWP
    ax.bar(x_array, y_array, bar_width, label="Total")

    # Set labels
    ax.set_ylabel(settings.labels.LCA_output_plotting_string)
    plt.xticks(rotation=45)

    # Display legend
    if legend_loc == "box":
        ax.legend()

    # Display plot
    plt.tight_layout()
    plt.show()

    return ax


def plot_single_process_GWP(GWP_df, process_name, bins=40, stacked=True, show_total=True):

    # Extract process
    process_series = GWP_df[process_name]

    # Get required parameters
    subprocess_names = np.array(process_series["subprocess_names"])
    subprocess_GWPs = np.array(process_series["subprocess_GWP"])

    # Get total marker coordinates
    if show_total:
        GWP_total = np.array(process_series["GWP"])
        marker_x = np.array(plt.hist(GWP_total, bins=bins, alpha=0, histtype='bar')[1][0:-1])
        marker_y = np.array(plt.hist(GWP_total, bins=bins, alpha=0, histtype='bar')[0])
        marker_threshold = settings.background.iterations_MC * 0.01  # threshold below which markers are not displayed

    # Plot
    sns.set_theme()  # Use seaborn style
    fig, ax = plt.subplots()
    ax.hist(subprocess_GWPs, bins=bins, histtype='bar', stacked=stacked, alpha=1, label=subprocess_names[0])

    # Plot total whilst excluding zeros or very low values for plotting
    if show_total:
        ax.scatter(marker_x[marker_y > marker_threshold], marker_y[marker_y > marker_threshold], label="Total",
                   marker="x", color="black", alpha=0.8)

    # Set legend, title, and labels
    ax.legend()
    ax.set_title(process_name)
    ax.set_xlabel(settings.labels.LCA_output_plotting_string)
    ax.set_ylabel("Monte Carlo Iterations")

    # Display plot
    plt.tight_layout()
    plt.show()
    # TODO: This function currently sometimes displays two figure objects (1 being empty). Not sure why this happens
    #  as the syntax is similar to other plotting functions.

    return ax


def plot_global_GWP_byprocess(GWP_df, bins=50):

    # Get GWP values
    GWP_matrix = []  # initialise storage list
    for count, column in enumerate(GWP_df.columns):
        GWP_matrix.append(GWP_df.loc["GWP", column])

    GWP_matrix = np.transpose(np.array(GWP_matrix))  # convert to right format
    GWP_exc_total = GWP_matrix[:, 0:-1]  # get list without the total
    GWP_total = GWP_matrix[:, -1]  # get list of total GWP

    # Turn bin number into a bin vector which can be used to plot histograms and total
    bin_width = round((np.max(GWP_matrix) - np.min(GWP_matrix)) / bins)
    min_value = math.floor(np.min(GWP_matrix))
    max_value = math.ceil(np.max(GWP_matrix))
    bin_vector = range(min_value, max_value + bin_width, bin_width)

    # Get total marker coordinates
    marker_x = np.array(plt.hist(GWP_total, bins=bin_vector, alpha=0, histtype='bar')[1][0:-1])
    marker_y = np.array(plt.hist(GWP_total, bins=bin_vector, alpha=0, histtype='bar')[0])
    marker_threshold = settings.background.iterations_MC * 0.01  # threshold below which markers are not displayed

    # Plot histograms and total
    sns.set_theme()  # Use seaborn style
    fig, ax = plt.subplots()

    # Plot histograms
    ax.hist(GWP_exc_total, bins=bin_vector, histtype='bar', stacked=True, label=GWP_df.columns[0:-1])

    # Plot total whilst excluding zeros or very low values for plotting
    ax.scatter(marker_x[marker_y > marker_threshold], marker_y[marker_y > marker_threshold], label=GWP_df.columns[-1],
               marker="x", color="black", alpha=0.8)

    # Set legend and labels
    ax.legend()
    ax.set_xlabel(settings.labels.LCA_output_plotting_string)
    ax.set_ylabel("Monte Carlo Iterations")

    # Display plot
    plt.tight_layout()
    plt.show()

    return ax
