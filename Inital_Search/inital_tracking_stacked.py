import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from Initial_tracking import prepare_samples

from statsmodels.nonparametric.smoothers_lowess import lowess

from scipy.signal import savgol_filter

if __name__ == "__main__":
    pos = [[],[],[],[],[],[]]
    pos[0] = prepare_samples("Pos1_16vinkel.csv").sort_values(by="POS")
    pos[1] = prepare_samples("Pos2_16vinkel.csv").sort_values(by="POS")
    pos[2] = prepare_samples("Pos3_16vinkel.csv").sort_values(by="POS")
    pos[3] = prepare_samples("Pos4_16vinkel.csv").sort_values(by="POS")
    pos[4] = prepare_samples("Pos5_16vinkel.csv").sort_values(by="POS")
    pos[5] = prepare_samples("Pos6_16vinkel.csv").sort_values(by="POS")
    for i in range(6):
        pos[i]["POS"] -= 215.0
        pos[i]["POS"] %= 360.0
        pos[i] = pos[i].sort_values(by="POS")



    fig, axes = plt.subplots(6, 1, figsize=(8, 12), sharex=True)  # sharex=True to align x-axis

    # Plot data on each subplot
    for i, ax in enumerate(axes):


        ax.scatter(pos[i]["POS"], pos[i]["RSSI"])
        ax.step(pos[i]["POS"], pos[i]["RSSI"], alpha=0.2)

        ax.set_ylabel(f'Pos {i+1}')




        max_idx = pos[i]["RSSI"].idxmax()
        max_x = pos[i]["POS"][max_idx]
        max_y = pos[i]["RSSI"][max_idx]
        

        ax.plot(max_x, max_y, 'ro')  # red dot

        res = lowess(pos[i]["RSSI"], pos[i]["POS"], frac=0.1)  

        ax.plot(pos[i]["POS"], res[:,1], linestyle='dashed', linewidth=2, color="black")



        ax.text(max_x-4, max_y*0.85, f'heading: {max_x:.2f}', color='red', fontsize=9,
        verticalalignment='center', horizontalalignment='right')
        ax.grid(True)

    axes[-1].set_xlabel('Heading [°]') #Xlabel kun på x aksen

    plt.tight_layout()
    plt.show()