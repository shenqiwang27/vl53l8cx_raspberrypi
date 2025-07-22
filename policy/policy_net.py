import torch
import torch.nn as nn


class CustomMLP(nn.Module):
    def __init__(self, input_dim=256+47, hidden_dim=256, output_dim=4):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, output_dim)
        self.activation = nn.ReLU()
        self.tanh = nn.Tanh()

    def forward(self, x):
        x = self.activation(self.fc1(x))
        x = self.activation(self.fc2(x))
        print(x.mean())
        x = self.fc3(x)
        return self.tanh(x)
 

class CustomLSTM(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size

        self.weight_ih = nn.Parameter(torch.empty(4 * hidden_size, input_size))
        self.weight_hh = nn.Parameter(torch.empty(4 * hidden_size, hidden_size))
        self.bias_ih = nn.Parameter(torch.empty(4 * hidden_size))
        self.bias_hh = nn.Parameter(torch.empty(4 * hidden_size))

        self.reset_parameters()

    def reset_parameters(self):
        
        stdv = 1.0 / (self.hidden_size ** 0.5)
        for weight in self.parameters():
            nn.init.uniform_(weight, -stdv, stdv)

    def forward(self, x, h_0=None, c_0=None):
        seq_len, batch_size, _ = x.shape

        if h_0 is None:
            h_t = torch.zeros(batch_size, self.hidden_size, device=x.device)
        else:
            h_t = h_0

        if c_0 is None:
            c_t = torch.zeros(batch_size, self.hidden_size, device=x.device)
        else:
            c_t = c_0

        outputs = []
        gates_per_timestep = [] 

        for t in range(seq_len):
            x_t = x[t]

            gates = (
                torch.matmul(x_t, self.weight_ih.T) + self.bias_ih +
                torch.matmul(h_t, self.weight_hh.T) + self.bias_hh
            )

            i, f, g, o = gates.chunk(4, dim=1)

            i = torch.sigmoid(i)  
            f = torch.sigmoid(f)  
            g = torch.tanh(g)     
            o = torch.sigmoid(o)  

            c_t = f * c_t + i * g
            h_t = o * torch.tanh(c_t)

            outputs.append(h_t.unsqueeze(0))

            gates_per_timestep.append({
                "input_gate": i.detach().cpu(),
                "forget_gate": f.detach().cpu(),
                "candidate": g.detach().cpu(),
                "output_gate": o.detach().cpu()
            })

        outputs = torch.cat(outputs, dim=0)  
        return outputs, (h_t, c_t), gates_per_timestep

def load_weights_from_lstm_actor(custom_lstm, state_dict, prefix='lstm_actor'):
    with torch.no_grad():
        custom_lstm.weight_ih.copy_(state_dict[f"{prefix}.weight_ih_l0"])
        custom_lstm.weight_hh.copy_(state_dict[f"{prefix}.weight_hh_l0"])
        custom_lstm.bias_ih.copy_(state_dict[f"{prefix}.bias_ih_l0"])
        custom_lstm.bias_hh.copy_(state_dict[f"{prefix}.bias_hh_l0"])
def load_weights_from_state_dict(custom_mlp, state_dict, prefix="mlp_extractor"):
    with torch.no_grad():
        custom_mlp.fc1.weight.copy_(state_dict[f"{prefix}.policy_net.0.weight"])
        custom_mlp.fc1.bias.copy_(state_dict[f"{prefix}.policy_net.0.bias"])
        custom_mlp.fc2.weight.copy_(state_dict[f"{prefix}.policy_net.2.weight"])
        custom_mlp.fc2.bias.copy_(state_dict[f"{prefix}.policy_net.2.bias"])
        custom_mlp.fc3.weight.copy_(state_dict["action_net.0.weight"])
        custom_mlp.fc3.bias.copy_(state_dict[f"action_net.0.bias"])
        
class ObsRMS(nn.Module):
    def __init__(self, obs_dim):
        super().__init__()

        self.mean = torch.zeros(obs_dim)
        self.var = torch.zeros(obs_dim)

    def load(self, path):
        data = torch.load(path, map_location='cpu')
        self.mean.copy_(data["mean"].squeeze())
        self.var.copy_(data["var"].squeeze())

        self.mean = self.mean[:12]
        self.var = self.var[:12]

    def normalize(self, obs):
        return (obs - self.mean) / torch.sqrt(self.var + 1e-8)

    def unnormalize(self, norm_obs):
        return norm_obs * torch.sqrt(self.var + 1e-8) + self.mean

