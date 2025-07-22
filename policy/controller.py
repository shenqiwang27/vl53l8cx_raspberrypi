import torch

def action_acc_bounding(actions):
    std_acc = 0.6
    mean_acc = 0.0
    
    return actions * std_acc + mean_acc