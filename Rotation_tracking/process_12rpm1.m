function [x_Testbed, y_Testbed, x_Platform, y_Platform, z] = process_12rpm1(testbedFile, platformFile)

    % Læs filer
    data_Testbed  = readtable(testbedFile,  "Delimiter", ";");
    data_Platform = readtable(platformFile, "Delimiter", ";");

    % Udpak data
    x_Platform = str2double(strrep(data_Platform{:,1}, ',', '.'));
    y_Platform = str2double(strrep(data_Platform{:,2}, ',', '.'));

    x_Testbed = str2double(strrep(data_Testbed{:,1}, ',', '.'));
    y_Testbed = str2double(strrep(data_Testbed{:,2}, ',', '.'));

    % Normaliser startpunkt
    y_Platform = y_Platform - y_Platform(1); 
    y_Testbed  = y_Testbed  - y_Testbed(1);

    % Korrigér rotationer i Testbed
    y_Testbed(51:end)  = y_Testbed(51:end)  - 360;
    y_Testbed(111:end) = y_Testbed(111:end) - 360;
    y_Testbed(171:end) = y_Testbed(171:end) - 360;

    % Gør data positivt
    y_Testbed = abs(y_Testbed);

    % Kombiner signaler
    z = y_Testbed + y_Platform;

    % Figur (kan fjernes hvis funktionen ikke skal plotte)
    % figure;
    % plot(x_Testbed, y_Testbed, x_Platform, y_Platform, x_Testbed, z)
    % legend('Testbed', 'Platform', 'Den sidste');
    % title('Processed Data')
    % xlabel('X')
    % ylabel('Y')

end
