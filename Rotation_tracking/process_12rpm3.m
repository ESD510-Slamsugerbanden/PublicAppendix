function [x_Testbed, y_Testbed, x_Platform, y_Platform, z] = process_12rpm3(testbedFile, platformFile)


data_3_Testbed = readtable(testbedFile, "Delimiter", ";");
data_3_Platform = readtable(platformFile, "Delimiter", ";");

A = data_3_Platform;
B = data_3_Testbed;

x_Platform = str2double(strrep(A{:,1}, ',', '.'));
y_Platform = str2double(strrep(A{:,2}, ',', '.'));

x_Testbed = str2double(strrep(B{:,1}, ',', '.'));
y_Testbed = str2double(strrep(B{:,2}, ',', '.'));

y_Platform = y_Platform - y_Platform(1); y_Testbed = y_Testbed-y_Testbed(1);


y_Testbed(63:end) = y_Testbed(63:end) -360;
y_Testbed(124:end) = y_Testbed(124:end) -360;
y_Testbed(184:end) = y_Testbed(184:end) -360;
y_Testbed = abs(y_Testbed);

z = y_Testbed + y_Platform;

% plot(x_Testbed, y_Testbed, x_Platform, y_Platform, x_Testbed, z)
% legend('Testbed', 'Platform', 'Den sidste');

end