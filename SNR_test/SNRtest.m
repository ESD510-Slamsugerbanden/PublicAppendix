clear all;
clc;

load("Data.mat");
ticks = [10,15,20,25,30,40,50,60,70,80,90,100,110,150];


floor = -88;
thermalfloor = -100;


SNRpr = SNrs.P_r-floor; 
SNRtarget = SNrs.Target-floor;

ThermalSNRpr = SNrs.P_r-thermalfloor;
ThermalSNRtarget = SNrs.Target-thermalfloor;

tiledlayout(2,1);

nexttile; 
plot(SNrs.Dist,SNRpr)
hold on;
plot(SNrs.Dist,SNRtarget)
hold off;
grid on;
legend("Measured SNR", "Calculated SNR")
title("SNR for interference floor")
xticks(ticks)
%yline(25,'--')
ylabel("SNR [dB]")
xlabel("Distance [m]")



nexttile;
plot(SNrs.Dist,ThermalSNRpr)
hold on;
plot(SNrs.Dist,ThermalSNRtarget)
hold off;
ylabel("SNR [dB]")
xlabel("Distance [m]")
xticks(ticks)
title("SNR for thermal floor")
grid();
legend("Measured SNR", "Calculated SNR")
