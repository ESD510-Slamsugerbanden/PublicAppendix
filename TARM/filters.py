import numpy as np
class Highpass:
    def __init__(self, w_n, T_s):
        
        self.w_n = w_n
        self.T_s = T_s
        self.y_1 = 0.0
        self.x_1 = 0.0

        alpha = self.w_n * self.T_s / 2.0
        self.a = (1.0 - alpha) / (1.0 + alpha)   # a1
        self.b = 1.0 / (1.0 + alpha)             # b0
        pass

    def filter(self, x):

        y = self.a * self.y_1 + self.b * (x - self.x_1)
        self.y_1 = y
        self.x_1 = x
        return y




class Lowpass:
    def __init__(self, w_n, T_s):
        self.w_n = w_n
        self.T_s = T_s
        self.y_1 = 0
        self.x_1 = 0

        self.a = (2 - w_n * T_s) / (2 + w_n * T_s)
        self.b = w_n * T_s / (2 + w_n * T_s)
    
    def filter(self, x):
        y = self.a * self.y_1 + self.b * (x + self.x_1)
        
        self.y_1 = y
        self.x_1 = x
        return y



##Blandede til at teste graverne
if __name__ == "__main__":
    import plotly.graph_objects as go

    T_s = 0.01
    step = np.concatenate((np.zeros(100), np.ones(100),np.zeros(100))) 
    t = np.arange(len(step))*T_s 
    step = step + np.sin(t*10)*0.06
    highpiss = Highpass(10, T_s)
    lowpass = Lowpass(10, T_s)
    
    result = []
    result2 = []
    for x in step:
        result.append(highpiss.filter(x))
        result2.append(lowpass.filter(x))


    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=step))
    fig.add_trace(go.Scatter(x=t, y=result))
    fig.add_trace(go.Scatter(x=t, y=result2))
    fig.show()
