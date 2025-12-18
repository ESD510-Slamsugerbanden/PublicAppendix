import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import ast
from stationary_accuracy_mechanical import prepare_samples


def prepare_samples(name: str):
    beam_offsets = np.array([-48, -15, 15, 48])    
    raws = pd.read_csv(name)
    
    res_rssi  = []
    res_angle = []

    for i in range(len(raws)):
        angle = raws["POS"][i]                               
        vector = ast.literal_eval(raws["RSSI"][i])               

        for x in range(4):
            res_rssi.append(vector[x])
            res_angle.append((angle + beam_offsets[x]) % 360)
    
    data = pd.DataFrame({
        "RSSI": np.float32(res_rssi),
        "POS":  np.float32(res_angle)
    })

    return data



if __name__ == "__main__":

    beam_offsets = np.array([-48, -15, 15, 48])    
    pos = [[],[],[],[],[],[]]
    
    pos[0] = prepare_samples("Pos1_16vinkel.csv").sort_values(by="POS")
    pos[1] = prepare_samples("Pos2_16vinkel.csv").sort_values(by="POS")
    pos[2] = prepare_samples("Pos3_16vinkel.csv").sort_values(by="POS")
    pos[3] = prepare_samples("Pos4_16vinkel.csv").sort_values(by="POS")
    pos[4] = prepare_samples("Pos5_16vinkel.csv").sort_values(by="POS")
    pos[5] = prepare_samples("Pos6_16vinkel.csv").sort_values(by="POS")

    pos[0]["RSSI"] /= pos[0]["RSSI"].max()
    pos[1]["RSSI"] /= pos[1]["RSSI"].max()
    pos[2]["RSSI"] /= pos[2]["RSSI"].max()
    pos[3]["RSSI"] /= pos[3]["RSSI"].max()
    pos[4]["RSSI"] /= pos[4]["RSSI"].max()
    pos[5]["RSSI"] /= pos[5]["RSSI"].max()



    
    theta_list = [
        np.deg2rad(pos[0]["POS"]),
        np.deg2rad(pos[1]["POS"]),
        np.deg2rad(pos[2]["POS"]),
        np.deg2rad(pos[3]["POS"]),
        np.deg2rad(pos[4]["POS"]),
        np.deg2rad(pos[5]["POS"])
    ]

    for theta in theta_list:
        theta -= np.deg2rad(215.0)
        theta %= np.deg2rad(360.0)

    r_list = [
        pos[0]["RSSI"],
        pos[1]["RSSI"],
        pos[2]["RSSI"],
        pos[3]["RSSI"],
        pos[4]["RSSI"],
        pos[5]["RSSI"]
    ]

    # -----------------------------------------------------
    # Plot them all on the SAME polar axis
    # -----------------------------------------------------
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, polar=True)

    colors = plt.cm.plasma(np.linspace(0, 1, len(theta_list)))
    i = 0
    for theta, r, c in zip(theta_list, r_list, colors):
        ax.plot(theta, r, linewidth=2, color=c, alpha=0.9, label=f"src: {i}")
        ax.fill(theta, r, color=c, alpha=0.25)   # adjust alpha for transparency
        i += 1
    ax.set_title("6 Overlapping Polar Plots with Different Angle Axes", pad=20)
    ax.legend()
    plt.show()
    #fig.savefig("polarplots.png", transparent=True)

    
    plt.show()