from policy_net import CustomLSTM, CustomMLP, ObsRMS
from policy_net import load_weights_from_lstm_actor, load_weights_from_state_dict
from controller import action_acc_bounding
import torch
import torch.nn as nn
import time
from .. import VL53L8CX
from ctypes import *
import numpy as np
import json

def tof_get_distance(tof):
    max_valid_range = 2500
    distance, target_status = tof.read_distance()
    distance_array = [distance[i] for i in range(64)]
    target_status_array = [target_status[i] for i in range(64)]

    distance_array = np.array(distance_array)
    target_status_array = np.array(target_status_array)
    valid_mask = (target_status_array == 5) | (target_status_array == 9)
    distance_array = np.where(valid_mask, distance_array, max_valid_range)
    distance_matrix = np.clip(np.where(distance_array < 0, max_valid_range, distance_array), 0, max_valid_range)
    distance_matrix = distance_matrix / max_valid_range
    distance_matrix = np.uint8(distance_matrix * 255)
    return torch.tensor(distance_matrix)

model_path = './policy_param.pth'
model = torch.load(model_path)
state_dict = model['state_dict']
rms_model_path = './rms.pth'

custom_lstm = CustomLSTM(input_size=64, hidden_size=256)
custom_mlp = CustomMLP()
load_weights_from_lstm_actor(custom_lstm, state_dict)
load_weights_from_state_dict(custom_mlp, state_dict)

rms = ObsRMS(obs_dim=24)
rms.load(rms_model_path)

tof = VL53L8CX.VL53L8CX()
goal_position = torch.tensor([10,10,1.5])
custom_hn,custom_cn = None, None

period = 0.1  # 100ms
next_time = time.monotonic()

while True:
    start_time = time.monotonic()

    tof_distance = tof_get_distance(tof)

    root_position = torch.tensor([0.0, 0.0, 0.0])
    linvels_body_frame = torch.zeros(3)
    angvels_body_frame = torch.zeros(3)
    root_euler_angles = torch.zeros(3)

    goal_dir = goal_position - root_position
    beta = torch.atan2(goal_dir[1], goal_dir[0])
    log_distance = torch.log(torch.norm(goal_dir[:2]) + 1e-6)  

    ext_input = torch.cat([
        log_distance,
        beta,
        goal_dir,
        linvels_body_frame,
        angvels_body_frame,
        root_euler_angles
    ])
    ext_input_norm = rms.normalize(ext_input)

    lstm_out, (custom_hn, custom_cn), _ = custom_lstm(tof_distance.unsqueeze(0).unsqueeze(0), custom_hn, custom_cn)
    custom_mlp_input = torch.cat([lstm_out.squeeze(0).squeeze(0), ext_input])
    custom_mlp_output = custom_mlp(custom_mlp_input)
    acc_command = action_acc_bounding(custom_mlp_output)

    next_time += period
    sleep_duration = next_time - time.monotonic()
    if sleep_duration > 0:
        time.sleep(sleep_duration)
    else:
        next_time = time.monotonic() + period

