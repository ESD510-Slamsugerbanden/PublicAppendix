import numpy as np
import matplotlib.pyplot as plt

from matplotlib.widgets import Slider




def get_rssi(theta):
    """Computes the expected RSSI for the 4 beam directions."""
    N = 4
    delta_phi = np.deg2rad([-135.66, -44.33, 43.33, 135.66])
    d_x = 0.4

    # The phase shifts by each element
    a = np.exp(-1j * 2 * np.pi * d_x * np.arange(N) * np.sin(theta))

    # Matrix with all combinations in the end
    combos = a[:, None] * np.exp(1j * np.outer(np.arange(N), delta_phi))

    # Sum across antennas for each beam setting
    array_factor = np.sum(combos, axis=0)

    # Sort of approximate antenna model
    Antenna = np.cos(theta / 2) ** 2

    return array_factor * Antenna 




def plot_array_factors():
    """Plots the 4 array factors on a polar plot."""
    theta = np.linspace(-np.pi, np.pi, 400)

    # Get 4 array factors for each theta
    AF = [get_rssi(angle) for angle in theta]
    AF = np.array(AF)   # shape = (1000, 4)
    AF = AF.T           # shape = (4, 1000)

    # Create polar plot
    fig = plt.figure(figsize=(8, 6))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    # Plot all 4 beams
    for i in range(4):
        pattern = np.abs(AF[i])
        pattern /= np.max(pattern)  # normalize
        ax.plot(theta, pattern, label=f"Array Factor {i+1}")

    ax.set_title("Polar Plot of 4 Array Factors", va='bottom')
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    plt.show()





if __name__ == "__main__":
    # Initial angle
    angle_target = np.deg2rad(10)
    d_theta = np.deg2rad(1)
    theta_samples = np.arange(4)
    samples = np.abs(get_rssi(angle_target))
    samples = samples - np.ones(len(samples)) * np.mean(samples)
    # Create figure and axis
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)  # Leave space for slider
    line, = ax.plot(theta_samples, samples, marker='o')
    ax.set_xlabel("Theta sample index")
    ax.set_ylabel("RSSI (abs)")
    ax.set_title("Interactive RSSI vs Angle")
    ax.set_ylim([-1, 1])


    # Define slider position [left, bottom, width, height]
    ax_angle = plt.axes([0.25, 0.1, 0.65, 0.03])
    slider_angle = Slider(ax_angle, 'Angle (deg)', -90, 90, valinit=np.rad2deg(angle_target))

    # Update function
    def update(val):
        angle_target = np.deg2rad(slider_angle.val)
        new_samples = np.abs(get_rssi(angle_target))
        new_samples = np.divide(new_samples, np.sum(new_samples))

        new_samples = new_samples - np.ones(len(new_samples)) * np.mean(new_samples)

        line.set_ydata(new_samples)

        fig.canvas.draw_idle()

    # Connect slider to update function
    slider_angle.on_changed(update)

    plt.show()
