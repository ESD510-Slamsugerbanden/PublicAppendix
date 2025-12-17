clear all;
clc;

% Læs data fra fil
data = readtable("Azimuth_TF.txt");
closedLoop_realData = readtable("Closed_loop_StepResponse.log");
closedLoop_realData = closedLoop_realData.AZ0_0_1 / (12811);

% Hent kolonner som arrays
time = (data{:,1} - 10032) / 1000;   
pos = data{:,2} / (6330*2);           % Azimuth counts
%pos = data{:,2};
t = time;
Ts = 10/1000 ;
t1 = (11362 - 10032) / 1000;  % Her hvor vi slukker for signal (ved 1 omgang)

t_pre = -0.5;                                 % hvor langt tilbage
time_ext = [t_pre:Ts:time(1)-Ts, time(:)'];

u = zeros(size(time_ext));
u =200*(time >= 0 & time < t1);
pos_ext = [zeros(1, sum(time_ext < time(1))), pos(:)'];

%u = 200 * double((time >= 0) & (time < t1));

dydx = gradient(pos)./gradient(t);


%% Målt data
% plot(time_ext, pos_ext, 'k')
% 
% yyaxis left
% ylabel("Revolutions")
% 
% yyaxis right
% plot(time_ext, u/200, 'k--')
% ylabel("Duty Cycle")
% ylim([-0.01 1.17])
% xlabel('Time (s)')
% xlim([-0.5, 1.8])
% grid on;
% legend('Measured position','Input signal')
% ax = gca;
% ax.YAxis(2).Color = 'k';


%% Modeller
data_id = iddata(dydx, u, Ts)
data_id2 = iddata(pos, u, Ts)
data_id = data_id(t<=t1)
data_id2 = data_id2(t<=t1)

sys1 = tfest(data_id, 1)
sys2 = tfest(data_id, 2)
sys3 = tfest(data_id, 3)

y1 = lsim(sys1, u, t);
y2 = lsim(sys2, u, t);
y3 = lsim(sys3, u, t);

s = tf('s'); 
sys1_pos = sys1 * (1/s);
sys2_pos = sys2 * (1/s);
sys3_pos = sys3 * (1/s);
y1_pos = lsim(sys1_pos, u, t);
y2_pos = lsim(sys2_pos, u, t);
y3_pos = lsim(sys3_pos, u, t);


%% Plotter Til lortet
   %  tiledlayout(2,1)
   %  nexttile
   %  hold on; grid on;
   % 
   %  plot(t, pos, 'k', 'DisplayName', 'Measured output');
   %  plot(t, y1_pos, 'b', 'DisplayName', '1. orden model');
   % % plot(t, y2_pos, 'r', 'DisplayName', '2. orden model');
   %  %plot(t, y3_pos, 'g', 'DisplayName', '3. orden model');
   %  plot(t, u/200, 'k--', 'DisplayName', 'Input');
   %  xlabel('Time [s]');
   %  ylabel('Position');
   %  title('Measured open-loop impulse response');
   %  xlim([0 t1+0.5]);
   %  legend show;
   %  hold off;
   % 
   % 
   %  nexttile
   %  hold on; grid on;
   %  plot(t, dydx, 'k', 'DisplayName', 'Measured output');
   % % plot(t, y1, 'b', 'DisplayName', '1. orden model');
   % % plot(t, y2, 'r', 'DisplayName', '2. orden model');
   %  %plot(t, y3, 'g', 'DisplayName', '3. orden model');
   %  %plot(t, u/200, 'k--', 'DisplayName', 'Input');
   %  xlabel('Tid [s]');
   %  ylabel('Hastighed (dpos/dt)');
   %  title('Model Fit vs Målt Data');
   %  xlim([0 t1]);
   %  legend show;
   %  hold off;

%% PID og closed loop

 PID = pid(1.3, 0.6, 0.16);
 %PID = pid(2, 0.5, 0.1); 
 sys_cl = feedback(sys1_pos, 1);
 sys_cl2 = feedback(sys1_pos * PID, 1);
% [y_step_cl, ~] = step(sys_cl, t);
% [y2_step_cl, ~] = step(sys_cl2, t);
% hold on; grid on;
% plot(t, y_step_cl, 'k', 'DisplayName', 'Without control');
% plot(t, y2_step_cl, 'r', 'DisplayName', 'With PID control');
% xlabel('Time [s]');
% ylabel('Amplitude');
% title('Simulated closed loop impuls-response');
% legend show;
% xlim([0, t1]);
% hold off;
 % step(sys_cl2)
%bode(sys_cl2)
%plot(t, u/200, 'k--', 'DisplayName', 'Input');

% L = 0.4;
% R = (0.959 - 0.0667) / (1-0.6)
% kp = 1.2 / (R*L)
% ki = 2*L
% Kd = 0.5*L





%% Graf 2 i rapport

Sim_TF = load("SImulink_TF.mat");
Sim_TF_PID = Sim_TF.data{1}.Values
Sim_TF_P = Sim_TF.data{2}.Values


%Sim_TF_time = Sim_TF.Time;

figure

% ----- Data -----
timeLortePis = (1:length(closedLoop_realData)) * 0.01;

% ----- Hovedplot -----
plot(timeLortePis, closedLoop_realData*360)
hold on
plot(Sim_TF_P.Time, Sim_TF_P.Data*360)
plot(Sim_TF_PID.Time, Sim_TF_PID.Data*360)

% ----- Stiplet reference -----
plot([0 1.45], [376 376], 'k--', 'LineWidth', 1.2)      % vandret
plot([1.45 1.45], [0 376], 'k--', 'LineWidth', 1.2)    % lodret
yt = yticks;                 % hent nuværende ticks
yticks(sort([yt 376]));      % tilføj 376 og sorter


xlim([0 2.5])
ylim([0 400])
ylabel('Position in degrees')
xlabel('Time (s)')
legend('Measured', 'Simulated with P=1', 'Simulated with PID')
title('Closed-loop step response')
grid on

% ----- Zoom-plot (nederst til højre) -----
ax_zoom = axes('Position',[0.52 0.25 0.35 0.3]); % [x y width height]
box on
hold on

plot(timeLortePis, closedLoop_realData*360)
plot(Sim_TF_P.Time, Sim_TF_P.Data*360)
plot(Sim_TF_PID.Time, Sim_TF_PID.Data*360)
axes(ax_zoom)   % gør zoom-axes aktiv

% plot([1.3 1.45], [376 376], 'k--', 'LineWidth', 1.2)
% plot([1.45 1.45], [340 376], 'k--', 'LineWidth', 1.2)

xlim([1.25 1.8])
ylim([340 380])

grid on
set(ax_zoom,'FontSize',8)
xlabel('')
ylabel('')
title('')
legend off
