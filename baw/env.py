import numpy as np


class Env():
    def __init__(self):
        self.player_state = [[i for i in range(9)] for _ in range(2)]  # player 남아있는 블록
        self.player_log = [[0 for i in range(24)] for _ in range(2)] # player 게임기록 (승or패)

        self.turn_action = [0, 0] # time_step action값
        self.first_player = 0 # 선플레이어 구분 변수

        self.score = [0, 0] # 승패 기록

        self.black_num = [5, 5] # 남은 흑 블록 수 (짝수)
        self.white_num = [4, 4] # 남은 백 블록 수 (홀수)


    def action(self, player, action):
        self.turn_action[player] = action
        self.player_state[player][action] = -1

        if action % 2 == 0:
            self.black_num[player] -= 1
        else:
            self.white_num[player] -= 1


    def get_state(self, player):
        # space 33
        # 이전 기록 + 남은 블럭수
        state = self.player_log[player] + self.player_state[player]

        # space 2
        # 상대 남은 흑 블럭수(0~5)
        # 상대 남은 백 블럭수(0~4)
        enemy_player = (player + 1) % 2
        state.append(self.black_num[enemy_player])
        state.append(self.white_num[enemy_player])

        # space 1
        # 선플(3)
        # 후플(흑or백)
        if player == self.first_player:
            state.append(3)
        else:
            state.append(0 if self.turn_action[enemy_player] % 2 == 0 else 1)

        return np.array(state)


    def update_step_log(self, time_step):
        winner = self.step_winner()
        index = time_step * 3
        states = []
        for player, p_log in enumerate(self.player_log):
            enemy_player = (player + 1) % 2
            p_log[index] = self.turn_action[player] # 나의 action 값
            p_log[index+1] = 0 if self.turn_action[enemy_player] % 2 == 0 else 1 # 상대 action 값(흑or백)
            p_log[index+2] = 1 if winner == player else 0 if winner != 3 else 3 # 승리시 1, 패배시 0, 무승부일시 3

        return states
        

    def step_winner(self):
        winner = 3
        if self.turn_action[0] > self.turn_action[1]:
            winner = 0
            self.first_player = 0
            self.score[winner] += 1
        elif self.turn_action[0] < self.turn_action[1]:
            winner = 1
            self.first_player = 1
            self.score[winner] += 1

        return winner


    def end_game_check(self):
        # 승점 5점시 게임 종룐
        if max(self.score) == 5:
            return True
        return False

