function [x_Testbed, y_Testbed, x_Platform, y_Platform, z] = process_12rpm2(testbedFile, platformFile)

data_2_Testbed = readtable(testbedFile, "Delimiter", ";");
data_2_Platform = readtable(platformFile, "Delimiter", ";");

A = data_2_Platform;
B = data_2_Testbed;

x_Platform = str2double(strrep(A{:,1}, ',', '.'));
y_Platform = str2double(strrep(A{:,2}, ',', '.'));

x_Platform = x_Platform(1:length(x_Platform)-2);
y_Platform = y_Platform(1:length(y_Platform)-2);


x_Testbed = str2double(strrep(B{:,1}, ',', '.'));
y_Testbed = str2double(strrep(B{:,2}, ',', '.'));

y_Platform = y_Platform - y_Platform(1); y_Testbed = y_Testbed-y_Testbed(1);

y_Testbed(54:end) = y_Testbed(54:end) - 360;
y_Testbed(113:end) = y_Testbed(113:end) - 360;
y_Testbed(173:end) = y_Testbed(173:end) - 360;
y_Testbed = abs(y_Testbed);


z = y_Testbed + y_Platform;

% plot(x_Platform,y_Platform, x_Testbed, y_Testbed, x_Platform, z);
% legend('Platform', 'Testbed', 'Platform lacking behind');

end