import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import ast
from scipy import stats
from scipy.stats import f_oneway


def prepare_samples(name: str, hp=True):
    raws = pd.read_csv(name)

    temp = [[0]*4]*len(raws)
    for i, raw in enumerate(raws["RSSI"]):
        temp[i] = ast.literal_eval(raw)  

    raws["RSSI"] = temp
    raws["Times"] -= raws["Times"].min()
    if hp:
        T_s_mean = np.mean(np.diff(raws["Times"]))
        temp = np.zeros(len(raws))
        for i, pos in enumerate(raws["POS"]):
            temp[i] = pos
        raws["POS"] = temp

    return raws


if __name__ == "__main__":
    
    stationary = [0,0,0,0]
    stationary[0] = prepare_samples("10metertest.csv", hp=True)
    stationary[1] = prepare_samples("20metertest.csv", hp=True)
    stationary[2] = prepare_samples("30metertest.csv", hp=True)
    stationary[3] = prepare_samples("40metertest.csv", hp=True)
    
    f_stat, p_val = f_oneway(stationary[0]["POS"], stationary[1]["POS"], stationary[2]["POS"], stationary[3]["POS"])
    print(f"fstat={f_stat}")
    print(f"pval={p_val}")

    stationary_long = prepare_samples("longftimetest.csv")
    #sns.lineplot(x=stationary_long["Times"], y=stationary_long["POS"])
    z_scores = stats.zscore(stationary_long["POS"])

    pos = []
    distance = []
    for i in range(len(stationary)):
        print(f"\"len{i}\",={len(stationary[i])} \t\"VAR{i}\"={stationary[i]["POS"].var()},\t\"2sigma{i}\"={stationary[i]["POS"].std()*2},\t\"MEAN{i}\"={stationary[i]["POS"].mean()}")

        pos = np.concatenate([pos, stationary[i]["POS"]])
        distance = np.concatenate([distance, np.ones(len(stationary[i]))*(i*10+10)])
    

    tracking_data = pd.DataFrame({"POS": pos, "DIST": distance})

    
    plt.figure(figsize=(9,6))
    sns.histplot(x= "POS",
                data=tracking_data,
                hue="DIST",
                kde=True)
    plt.grid(True)
    #sns.lineplot(data=tracking_data, x="DIST", y="POS")
    #plt.savefig("Histograms_with_Multiple_Density_lines_Seaborn_histplot.jpg")
    #fig, axes = plt.subplots(2, 2, figsize=(10, 10))

    #for i, ax in enumerate(axes.flatten()):
    #    stats.probplot(stationary[i]["POS"], dist="norm", plot=ax)
    #    ax.set_title(f"QQ, Positional estimates {10+i*10} meter")
    #    
    #plt.tight_layout()



    plt.show()