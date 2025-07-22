import torch 

def float_angle_nomalize(angle):
    return angle - 2 * torch.pi * torch.floor((angle + torch.pi) / (2 * torch.pi))


class ReferenceBase:
    def __init__(self, config, num_envs, device):
        self.device = device
        self.euler_angles = torch.zeros(3, dtype=torch.float32, device=self.device).tile((num_envs, 1))
        self.rates = torch.zeros(3, dtype=torch.float32, device=self.device).tile((num_envs, 1))
        self.accel = torch.zeros(3, dtype=torch.float32, device=self.device).tile((num_envs, 1))

        self.model_omega = torch.tensor(config.stabilization_attitude_ref_omega, dtype=torch.float32, device=self.device).tile((num_envs, 1))
        self.model_zeta = torch.tensor(config.stabilization_attitude_ref_zeta, dtype=torch.float32, device=self.device).tile((num_envs, 1))
        self.saturation_max_rate = torch.tensor(config.stabilization_attitude_ref_max, dtype=torch.float32, device=self.device).tile((num_envs, 1))
        self.saturation_max_accel = torch.tensor(config.stabilization_attitude_ref_max_omege_dot, dtype=torch.float32, device=self.device).tile((num_envs, 1))

    def attitude_ref_euler_float_update(self, sp_eulers, dt):
        # delta_rates = self.rates * dt
        # self.euler_angles += delta_rates
        # print('reference rates: ', self.rates[0])
        # print('reference euler_angles: ', self.euler_angles[0])
        self.update_euler_angles(dt)
        # print('updated reference euler_angles: ', self.euler_angles[0])
        self.euler_angles[:, 2] = float_angle_nomalize(self.euler_angles[:, 2])

        # integrate reference rotational speed
        delta_accel = self.accel * dt
        self.rates += delta_accel

        # compute reference attitude error
        attitude_error = self.euler_angles - sp_eulers
        attitude_error[:, 2] = float_angle_nomalize(attitude_error[:, 2])

        # compute reference angular accelerations
        self.accel = -2.0 * self.model_omega * self.model_zeta * self.rates - self.model_omega**2 * attitude_error
        # saturate angular accelerations
        self.attitude_ref_float_saturate_naive()

    def attitude_ref_float_saturate_naive(self):
        self.accel = torch.where(self.accel > self.saturation_max_accel, self.saturation_max_accel, self.accel)
        self.accel = torch.where(self.accel < -self.saturation_max_accel, -self.saturation_max_accel, self.accel)

        self.rates = torch.where(self.rates >= self.saturation_max_rate, self.saturation_max_rate, self.rates)
        self.accel = torch.where((self.rates >= self.saturation_max_rate) & (self.accel > 0.0), 0.0, self.accel)
        self.rates = torch.where(self.rates <= -self.saturation_max_rate, -self.saturation_max_rate, self.rates)
        self.accel = torch.where((self.rates <= -self.saturation_max_rate) & (self.accel < 0.0), 0.0, self.accel)

    def update_euler_angles(self, dt):
        phi, theta, psi = self.euler_angles[:, 0], self.euler_angles[:, 1], self.euler_angles[:, 2]
        p, q, r = self.rates[:, 0], self.rates[:, 1], self.rates[:, 2]

        M = torch.zeros((self.euler_angles.shape[0], 3, 3), device=self.device)
        M[:, 0, 0] = 1
        M[:, 1, 1] = torch.cos(phi)
        M[:, 0, 2] = -torch.sin(theta)
        M[:, 1, 2] = torch.sin(phi) * torch.cos(theta)
        M[:, 2, 1] = -torch.sin(phi)
        M[:, 2, 2] = torch.cos(phi) * torch.cos(theta)

        rates_matrix = torch.stack((p, q, r), dim=1)
        euler_dot = torch.bmm(M, rates_matrix.unsqueeze(-1)).squeeze(-1)

        self.euler_angles += euler_dot * dt

    def reset_reference(self, env_ids, euler_angles, rates):
        # print('reset_reference euler_angles: ', self.euler_angles[0])
        # print('env_ids: ', env_ids)
        self.euler_angles[env_ids] = euler_angles
        self.rates[env_ids] = rates
        self.accel[env_ids] = torch.zeros(3, dtype=torch.float32, device=self.device)

# angle = torch.tensor([[3.15, 4, 3, 1], [3.15, 4, 3, 1]], dtype=torch.float32)
# aa = float_angle_nomalize(angle)
# print(aa)
# print(angle)
