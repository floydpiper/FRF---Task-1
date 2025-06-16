import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# Get files
file_path_emlid = "data/528/528rtk.pos"
file_path_rtk = "data/528/YF2Reachm2_raw_20240528115238_emlid.pos"


def find_data_start(file_path):
    """ This function determines how many lines of the pos file to skip, as the first x begin with %

    Args:
        file_path (string): The file path of either emlid or rtk 

    Returns:
        i (int): Number of rows to skip
    """

    # Grabs the first column of the pos file
    data_full = np.genfromtxt(file_path, delimiter=' ', dtype=str, usecols=(0,), invalid_raise=False)

    i = 0
    for row in data_full:
        
        if "202" in row:
            i -= 1
            return i
        i += 1
        



# Load in files and filter out to only select Q1
def load_pos_file(file_path):
    """ This function filters out the columns to only select relevant data that is Q1

    Args:
        file_path (string): The file path of either emlid or rtk 

    Returns:
        data (numpy array): [timestamp, longitude, altitude]
    """

    # Number of rows to skip
    skip_rows = find_data_start(file_path)  

    # Col[1]: Timestamp, Col[3]: Longitude, Col[4]: Altitude, Col[5]: Quality 
    values = pd.read_csv(file_path, delimiter=r"\s+", skiprows=skip_rows, usecols=[1, 3,4,5], engine="python").to_numpy()


    data = []
    for row in values:

        # If Q1, add timestamp, longitude and altitude to the data array 
        if int(row[3]) == 1: 
            data.append([row[0], float(row[1]), float(row[2])])  

    return np.array(data)





def compare_timestamps(pre_emlid, pre_rtk):
    """ This function compares the timestamps between emlid and rtk to ensure that the rows are matched between the two arrays 

    Args:
        pre_emlid (numpy array): output from load_pos_fle
        pre_rtk (numpy array): output from load_pos_fle

    Returns:
        emlid_to_plot (numpy array): Used to plot in plot_positions_2d
        rtk_to_plot  (numpy array):  Used to plot in plot_positions_2d
        emlid_bias (numpy array):    Altitude values that have corresponding timestamp with quality 1 
        rtk_bias (numpy array):      Altitude values that have corresponding timestamp with quality 1 
    """

    # Init variables 
    emlid_to_plot = []
    rtk_to_plot = []

    emlid_bias = []
    rtk_bias = []

    rtk_dict = {row[0]: row for row in pre_rtk}



    for row in pre_emlid:

        # Grab the timestamp
        time_only = row[0]  


        if time_only in rtk_dict:  

            # Timestamp match between emlid and rtk
            matched_rtk_row = rtk_dict[time_only]  

            # Used to plot in plot_positions_2d
            emlid_to_plot.append([float(row[1]), float(row[2])])  
            rtk_to_plot.append([float(matched_rtk_row[1]), float(matched_rtk_row[2])])  
           
            # Altitude values that have corresponding timestamp with quality 1 
            emlid_bias.append([float(row[2])])  
            rtk_bias.append([float(matched_rtk_row[2])]) 

    return np.array(emlid_to_plot), np.array(rtk_to_plot), np.array(emlid_bias), np.array(rtk_bias)






# Grab Q1 and Q2
def find_quality(file_path):
    """ This function counts the number of Q1 and Q2 values in the pos file and calculates its percentage 

    Args:
        file_path (string): The file path of either emlid or rtk 

    Returns:
        data (numpy array): [percentage of Q1, percentage of Q2]
    """
    skip_rows = find_data_start(file_path)  
    values = pd.read_csv(file_path, delimiter=r"\s+", skiprows=skip_rows, usecols=[5], engine="python").to_numpy()

    # Init variables
    total = 0
    q1 = 0
    q2 = 0


    # Determine if Q1 or Q2
    for row in values:

        if int(row[0]) == 1: 
            q1 += 1
        elif int(row[0]) == 2:
            q2 += 1
        total += 1


    # Convert to percentage
    q1_percent = (q1/total)*100
    q2_percent = (q2/total)*100
    data = [q1_percent, q2_percent]

    return np.array(data)





def calc_diff(emlid, rtk):
    """ This function calculates the average height difference between emlid and rtk

    Args:
        emlid (numpy array): output from load_pos_file
        rtk (numpy array): output from load_pos_file

    Returns:
        diff_plot (numpy array): [longitude, difference in height]
        avg (var): overall average difference in height
    """


    emlid_plot, _, emlid_bias, rtk_bias = compare_timestamps(emlid, rtk)
    
    # Use emlid_plot to extract the longitude values 
    longitude = [sub_array[0] for sub_array in emlid_plot]

    # Calculate the absolute height difference between each row of emlid and rtk. Results in an array
    diff = np.abs(np.array(emlid_bias) - np.array(rtk_bias))  

    # Compute the average difference in the array. Results in a var
    avg = np.mean(diff)

    # Used to plot in plot_height_diff
    diff_plot = np.column_stack((longitude, diff))
    

    return diff_plot, avg




def plot_positions_2d(emlid, rtk):
    """ This is a plot of Altitude vs. Longitude of both emlid and rtk of Q1

    Args:
        emlid (numpy array): output from load_pos_file
        rtk (numpy array): output from load_pos_file
    """

    emlid_plot, rtk_plot, _, _ = compare_timestamps(emlid, rtk)

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.plot(emlid_plot[:, 0], emlid_plot[:, 1], 'b.', label='Emlid', markersize=1.5)
    ax.plot(rtk_plot[:, 0], rtk_plot[:, 1], 'r.', label='RTK', markersize=1.5)

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Altitude')
    ax.set_title('2D Position Comparison: Quality 1')
    ax.legend()
    ax.grid(True)

    plt.show()






def plot_quality(emlid_q, rtk_q):
    """ Histogram of the percentages of Q1 and Q2 in the pos file of both emlid and rtk

    Args:
        emlid_q (numpy array): output of find_quality 
        rtk_q (numpy array): output of find_quality 
    """
    
    fig, ax = plt.subplots()
    
    _, diff = calc_diff(emlid, rtk)
    diff_text = "Average difference: " + str(diff) + " meters"
    quality = ['Q1', 'Q2']
    x = np.arange(len(quality)) 
    width = 0.35  

    bar_labels = ['Emlid (With antenna correction)', 'RTK with patch']
    bar_colors = ['tab:red', 'tab:blue']

    bars1 = ax.bar(x - width/2, emlid_q, width, label=bar_labels[0], color=bar_colors[0])
    bars2 = ax.bar(x + width/2, rtk_q, width, label=bar_labels[1], color=bar_colors[1])

    
    # Add text labels on top of each bar
    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{bar.get_height():.1f}', 
                ha='center', va='bottom', color='black', fontsize=12, fontweight='bold')

    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{bar.get_height():.1f}', 
                ha='center', va='bottom', color='black', fontsize=12, fontweight='bold')
    text = fig.text(0.50, 0.02, diff_text, horizontalalignment='center', wrap=True ) 

    ax.set_xticks(x)
    ax.set_xticklabels(quality)
    ax.set_ylabel('Percent of quality')
    ax.set_title('Count of Q1 vs Q2')
    ax.legend(title='Source')

    plt.show()


# Plot difference in height over longitude 
def plot_height_diff(emlid, rtk):
    """ Graph of the height difference vs longitude

    Args:
        emlid (numpy array): output from load_pos_file
        rtk (numpy array): output from load_pos_file
    """


    diff_plot, _ = calc_diff(emlid, rtk) 

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)


    y = diff_plot[:, 0]  # Longitude
    z = diff_plot[:, 1]  # Altitude

    print("Longitude: ", diff_plot[:,0])
    print("Height difference: ",z)
    ax.plot(y, z, 'b.', label='Difference in height')


    ax.set_xlabel('Longitude')
    ax.set_ylabel('Height Difference')
    ax.set_title('Altitude difference vs. Longitude')
    ax.legend()


    plt.show()






def plot_avg_height():
    """Plots height differences 
    
    """

    x = [2030504,20230913,20240103,20240227,20240229]
    # create an index for each tick position
    xi = list(range(len(x)))
    with_correction = [8.36,6.82,7.14,6.55,6.72]
    without_correction = [3.49,1.10, 1.58, 0.52, 0.70]
    both_emlid = [6.57, 6.56, 6.54, 6.54, 6.57]
    # rkn2rtkp = [0,0,0,0,0]
    plt.ylim(0.5,8.5)
    # plot the index for the x-values
    plt.plot(xi, with_correction, marker='o', linestyle='--', color='r', label='Emlid (With antenna correction) vs. RTK') 
    plt.plot(xi, without_correction, marker='o', linestyle='--', color='b', label='Emlid (Without antenna correction) vs. RTK') 
    plt.plot(xi, both_emlid, marker='o', linestyle='--', color='g', label='Emlid (With antenna correction) vs. Emlid (Without antenna correction)') 
    # plt.plot(xi, rkn2rtkp, marker='o', linestyle='--', color='p', label='rkn2rtkp (With antenna correction) vs. rkn2rtkp (Without antenna correction)') 
    plt.xlabel('Date')
    plt.ylabel('Change in height') 
    plt.xticks(xi, x)
    plt.title('Comparing Height Differences')
    plt.legend() 
    plt.show()




#Load data and plot
emlid = load_pos_file(file_path_emlid)
rtk = load_pos_file(file_path_rtk)
plot_positions_2d(emlid, rtk)

emlid_q = find_quality(file_path_emlid)
rtk_q = find_quality(file_path_rtk)
plot_quality(emlid_q, rtk_q)

plot_height_diff(emlid, rtk)

plot_avg_height()
