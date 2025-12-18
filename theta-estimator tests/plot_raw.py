import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time
import datetime
from scipy.stats import norm
import ast

def prepare_sample(name: str):
    data = pd.read_csv(name)
    data["Angles"] = np.rad2deg(data["Angles"])

    dt = datetime.datetime(2025, 11, 26, 13, 39, 30)
    data["Times"] = data["Times"] - dt.timestamp() + 433 #437.5
    data["real"] = np.heaviside(data["Times"], 0)*-3 * data["Times"]

    data["RSSI"] = data["RSSI"].apply(lambda x: np.fromstring(x.strip("[]"), sep=" ")) 

    return data

if __name__ == "__main__":


    #mask = data["Times"] > 0
    #X = data['Times'][mask]
    #Y = data['POS'][mask]
    
    # Calculate slope (m) and intercept (b) using polyfit
    #m, b = np.polyfit(X, Y, deg=1)  # deg=1 for linear regression
    #print(f"Slope (m): {m:.2f}")
    #print(f"Intercept (b): {b:.2f}")

    data = prepare_sample("./raw/133930.csv")

    #data['POS'] = data["POS"] * -3/m

    data['error'] = data['real'] - data["POS"]
    mu, sigma = norm.fit(data['error'])
    

    temp = [ ]
    
    for i in range(len(data)):
        vec = data['RSSI'][i]
        len_vec = np.sqrt(np.sum(vec**2))

        temp.append((vec[2]+vec[3]-vec[0]-vec[1])*60/len_vec)
        
    data["power_sub"] = temp


    temp = []
    beam_offsets = np.array([-48, -15, 15, 48])    

    for i in range(len(data)):
        vec = data['RSSI'][i]
        temp.append(beam_offsets[np.argmax(vec)])

    data["argmax"] = temp


    sns.lineplot(data=data, x="Times", y="POS", errorbar=("ci", 95))
    sns.lineplot(data=data, x="Times", y="Angles", errorbar=("ci", 95))
    sns.lineplot(data=data, x="Times", y="argmax", errorbar=("ci", 95))
    sns.lineplot(data=data, x="Times", y="power_sub", errorbar=("ci", 95))
    sns.lineplot(data=data, x="Times", y="real", errorbar=("ci", 95))
    plt.show()

    
    data["e_dot"]       = data["Angles"] - data['real']
    data["e_argmax"]    = data["argmax"] - data['real']
    data["e_power_sub"] = data["power_sub"] - data['real']

    mask = (data["Times"] < 23)

    data["e_dot"]       = data["e_dot"][mask]
    data["e_argmax"]    = data["e_argmax"][mask]
    data["e_power_sub"] = data["e_power_sub"][mask]

    #sns.lineplot(data=data, x="Times", y="e_dot", errorbar=("ci", 95))
    #sns.lineplot(data=data, x="Times", y="e_argmax", errorbar=("ci", 95))
    #sns.lineplot(data=data, x="Times", y="e_power_sub", errorbar=("ci", 95))

    temp =[]
    algorithm = ["dot"]*len(data["e_dot"]) + ["e_argmax"]*len(data["e_argmax"]) + ["pwrsub"]*len(data["e_power_sub"])
    
    temp = np.concatenate([temp,data["e_dot"]])
    temp = np.concatenate([temp,data["e_argmax"]])
    temp = np.concatenate([temp,data["e_power_sub"]])

    errors = pd.DataFrame({"error": temp, "algorithm": algorithm})

    sns.histplot(x= "error",
            data=errors,
            hue="algorithm",
            kde=True,
            bins=30)
    plt.grid(True)
    #sns.histplot(data=data, x="error", stat="density", bins=30, kde=False, color='lightblue')


    # Generate x values for the fitted curve
    #sns.histplot(data=data, x="error", stat="density", bins=30, kde=False, color='lightblue')
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 200)
    p = norm.pdf(x, mu, sigma)
    
    #plt.plot(x, p, 'r', linewidth=2)
    #plt.xlim([-15, 24])
    #plt.ylim([-75, 50])

    
    
    


    
    plt.show()

    
