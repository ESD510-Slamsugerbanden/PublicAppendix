clear all;
clc;
close all;


[x_Testbed_rpm1, y_Testbed_rpm1, x_Platform_rpm1, y_Platform_rpm1, z_rpm1] = process_12rpm1("Data\12rpm1_data_Testbed.txt", "Data\12rpm1_data_platform");
[x_Testbed_rpm2, y_Testbed_rpm2, x_Platform_rpm2, y_Platform_rpm2, z_rpm2] = process_12rpm2("Data\12rpm2_data_Testbed.txt", "Data\12rpm2_data_platform");
[x_Testbed_rpm3, y_Testbed_rpm3, x_Platform_rpm3, y_Platform_rpm3, z_rpm3] = process_12rpm3("Data\12rpm3_data_Testbed.txt", "Data\12rpm3_data_platform");

y_platform_all = [y_Platform_rpm1(61:225); y_Platform_rpm2(61:225); y_Platform_rpm3(61:225)];


mean_platform = (y_Platform_rpm1(1:length(y_Testbed_rpm1)) + y_Platform_rpm2(1:length(y_Testbed_rpm1)) + y_Platform_rpm3(1:length(y_Testbed_rpm1))) / 3;
mean_Testbed = (y_Testbed_rpm1(1:length(y_Testbed_rpm1)) + y_Testbed_rpm2(1:length(y_Testbed_rpm1)) + y_Testbed_rpm3(1:length(y_Testbed_rpm1))) / 3;

mean_z = mean_Testbed + mean_platform;

tiledlayout(1,2)

nexttile
plot(x_Testbed_rpm1, y_Testbed_rpm1)
hold on
plot(x_Testbed_rpm2, y_Testbed_rpm2)
plot(x_Testbed_rpm3, y_Testbed_rpm3)

plot(x_Testbed_rpm1, mean_z, 'k:', LineWidth=2.5)
ylim([0, 1300]);
xlim([0, 22]);
grid on
legend('Testbed 1. meas.', 'Testbed 2. meas.', 'Testbed 3. meas.', 'Platform mean')
hold off
title('Azimuth Testbed position (\theta ), & mean platform position')
xlabel('Time (s)')
ylabel('Position (\theta) in degrees')

nexttile
plot(x_Platform_rpm1, y_Platform_rpm1)
hold on;
plot(x_Platform_rpm2, y_Platform_rpm2);
plot(x_Platform_rpm3, y_Platform_rpm3);
plot(x_Platform_rpm1, mean_platform, 'k:', 'LineWidth', 2.5);
grid on;
xlim([0, 22])
xlabel('time (s)')
ylabel('Position (\theta) in degrees')
title({'Azimuth platform \theta error', 'with respect to the testbed'})
legend('1. meas.', '2. meas.', '3. meas.', 'Mean')



