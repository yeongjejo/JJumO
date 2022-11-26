import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import os


# Hyperparameters
learning_rate = 0.00001
gamma = 0.99
T_horizon = 10
clip_rho_threshold = 1.0
clip_c_threshold = 1.0


class VtraceP1(nn.Module):
    def __init__(self, num, load_check):
        super(VtraceP1, self).__init__()
        self.data = []

        self.fc1 = nn.Linear(66, 512)
        self.fc2 = nn.Linear(512, 512)
        self.fc_pi = nn.Linear(512, 16)
        self.fc_v = nn.Linear(512, 1)
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        self.dropout = nn.Dropout(0.3) # overfitting 방지용....

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        self.clip_rho_threshold = torch.tensor(clip_rho_threshold, dtype=torch.float).to(self.device)
        self.clip_c_threshold = torch.tensor(clip_c_threshold, dtype=torch.float).to(self.device)

        self.chkpt_file = os.path.join("D:\Pixel_log\PPO\p1", 'player1-' + str(num) + '.pt')
        print(num)
        if load_check and num < 15:
            self.load_model()


    def softmax(self, input):
        c = torch.max(input)  # overflow 방지를위한 변수
        exp_a = torch.exp(input - c)  # overflow 대책
        sum_exp_a = torch.sum(exp_a)
        y = exp_a / sum_exp_a
        return y

    def pi(self, x, softmax_dim=0):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc_pi(x)
        prob = F.softmax(x, dim=softmax_dim)

        return prob

    def v(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        v = self.fc_v(x)
        return v

    def put_data(self, transition):
        self.data.append(transition)

    def make_batch(self):
        s_lst, a_lst, r_lst, s_prime_lst, mu_a_lst, done_lst = [], [], [], [], [], []
        for transition in self.data:
            s, a, r, s_prime, mu_a, done = transition

            s_lst.append(s)
            a_lst.append([a])
            r_lst.append([r])
            s_prime_lst.append(s_prime)
            mu_a_lst.append([mu_a])
            done_mask = 0 if done else 1
            done_lst.append([done_mask])

        s, a, r, s_prime, done_mask, mu_a = torch.tensor(s_lst, dtype=torch.float).to(self.device), torch.tensor(a_lst).to(self.device), \
                                            torch.tensor(r_lst).to(self.device), torch.tensor(s_prime_lst, dtype=torch.float).to(self.device), \
                                            torch.tensor(done_lst, dtype=torch.float).to(self.device), torch.tensor(mu_a_lst).to(self.device)
        self.data = []
        return s, a, r, s_prime, done_mask, mu_a

    def vtrace(self, s, a, r, s_prime, done_mask, mu_a):
        with torch.no_grad():
            pi = self.pi(s, softmax_dim=1)
            pi_a = pi.gather(1, a)
            v, v_prime = self.v(s), self.v(s_prime)
            # print(pi_a)
            # print(pi)
            ratio = (torch.log(pi_a + 1e-10)- torch.log(mu_a + 1e-10)).sum(1, keepdim=True)
            # print(ratio)
            ratio = ratio.clamp_(max=87).exp()
            # ratio = torch.exp(torch.log(pi_a + 1e-10)- torch.log(mu_a + 1e-10)) # a/b == exp(log(a)-log(b))
            # print(ratio)

            rhos = torch.min(self.clip_rho_threshold, ratio).cpu()
            cs = torch.min(self.clip_c_threshold, ratio).cpu().numpy()
            td_target = r + gamma * v_prime * done_mask
            delta = rhos * (td_target - v).cpu().numpy()

            vs_minus_v_xs_lst = []
            vs_minus_v_xs = 0.0
            vs_minus_v_xs_lst.append([vs_minus_v_xs])

            for i in range(len(delta) - 1, -1, -1):
                vs_minus_v_xs = gamma * cs[i][0] * vs_minus_v_xs + delta[i][0]
                vs_minus_v_xs_lst.append([vs_minus_v_xs])
            vs_minus_v_xs_lst.reverse()

            vs_minus_v_xs = torch.tensor(vs_minus_v_xs_lst, dtype=torch.float)
            vs = vs_minus_v_xs[:-1] + v.cpu().numpy()
            vs_prime = vs_minus_v_xs[1:] + v_prime.cpu().numpy()
            advantage = (r + gamma).cpu() * vs_prime.cpu() - v.cpu().numpy()

        return vs, advantage, rhos

    def train_net(self):
        s, a, r, s_prime, done_mask, mu_a = self.make_batch()
        vs, advantage, rhos = self.vtrace(s, a, r, s_prime, done_mask, mu_a)

        pi = self.pi(s, softmax_dim=1)
        pi_a = pi.gather(1, a)

        val_loss = F.smooth_l1_loss(self.v(s), vs.cuda())
        pi_loss = -rhos.to(self.device) * torch.log(pi_a + 1e-10).to(self.device) * advantage.to(self.device)
        loss = pi_loss + val_loss

        self.optimizer.zero_grad()
        loss.mean().backward()
        self.optimizer.step()

        # print('pp1')
        print(loss.mean())
        # print(loss.mean())


    def save_model(self):
        torch.save(self.state_dict(), self.chkpt_file)

    def load_model(self):
        self.load_state_dict(torch.load(self.chkpt_file))

