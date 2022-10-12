class Env():
    def __init__(self):
        self.player_state = [[i for i in range(9)] for _ in range(2)]  # player 남아있는 블록
        self.player_log = [[0 for i in range(24)] for _ in range(2)] # player 게임기록 (승or패)

        self.turn_action = [0, 0] # time_step action값
        self.first_player = 0 # 선플레이어 구분 변수


    def action(self, player, action):
        self.turn_action[player] = action
        self.player_state[player][action] = -1


    def get_state(self, player):
        # space 33
        # 이전 기록 + 남은 블럭수
        state = self.player_log[player] + self.player_state[player]
        enemy_player = (player + 1) % 2

        # space 2
        # 상대 남은 흑 블럭수(0~5)
        # 상대 남은 백 블럭수(0~4)
        even_num = 0 # 짝수
        odd_num = 0 # 홀수
        for i in self.player_state[enemy_player]:
            if i > -1:
                if i % 2 == 0:
                    even_num += 1
                else:
                    odd_num += 1
        state.append(even_num)
        state.append(odd_num)

        # space 1
        # 선플(3)
        # 후플(흑or백)
        if player == self.first_player:
            state.append(3)
        else:
            state.append(0 if self.turn_action[enemy_player] % 2 == 0 else 1)

        return state


    def aet_state(self, time_step, winner):
        enemy_player = (player + 1) % 2
        index = time_step * 3
        for player, p_log in enumerate(self.player_log):
            p_log[index] = self.turn_action[player]
            p_log[index+1] = 0 if self.turn_action[enemy_player] % 2 == 0 else 1


    def step_winner(self, time_step):
        winner = 3
        if self.turn_action[0] > self.turn_action[1]:
            winner = 0
        elif self.turn_action[0] < self.turn_action[1]:
            winner = 1

        return 1



