
class Pixel():
    def __init__(self):
        # Map setting
        self.map = [[0 for _ in range(8)] for _ in range(8)]
        self.map[0][0] = 3
        self.map[0][7] = 3
        self.map[7][0] = 3
        self.map[7][7] = 3
        self.map[3][3] = 1
        self.map[4][4] = 2
        self.x_point, self.y_point = 3, 3

        self.player1_count = 0
        self.player2_count = 0

        self.reward_cul_check = True
        self.reward_point_1 = [
            [2, 1, 1, 1, 0],
            [0, 1, 1, 1, 2],
            [0, 1, 1, 1, 0],
        ]
        self.reward_point_2 = [
            [1, 1, 1, 0, 0],
            [1, 1, 1, 0, 1],
            [1, 1, 1, 0, 2],
            [1, 1, 1, 2, 2],
            [1, 1, 1, 2, 0],
            [1, 1, 1, 2, 1],
        ]

    # action 맵에 등록(?)
    # 돌 둘곳 선택
    # action 범위 0~15
    # 0 ~ 7 x 좌표 높을 수록 오른쪽
    # 8 ~ 15 y 좌표 높을 수록 아래쪽
    def set_action(self, player, action):
        xp, yp = self.x_point, self.y_point
        if action < 8:
            xp = action
        else:
            yp = int(action % 8)

        if self.map[yp][xp] == 0:
            self.x_point = xp
            self.y_point = yp
            self.map[self.y_point][self.x_point] = player
            return True
        else:
            return False

    def re_action_set(self, action, prob):
        prob[action] = 0.0

        # 더이상 둘곳이 없으면 무승부
        if max(prob) <= 0.:
            # print(111111111111111111111111111111111111111111111111111111111111)
            # print(prob)
            return prob, 0, True

        return prob, np.argmax(prob), False

    # 게임 승리 확인
    def check_win(self, player):
        row = self.check_row(self.x_point, self.y_point, player)
        col = self.check_col(self.x_point, self.y_point, player)
        left_diagonal = self.check_left_diagonal(self.x_point, self.y_point, player)
        right_diagonal = self.check_right_diagonal(self.x_point, self.y_point, player)

        # 4개이상 이어져 있을시 True 리턴
        if row >= 4 or col >= 4 or left_diagonal >= 4 or right_diagonal >= 4:
            return True

        # 무승부를 대비하여 3개 이상 이어져 있는 횟수 누적
        if player == 1:
            if row == 3:
                self.player1_count += 1
            if col == 3:
                self.player1_count += 1
            if left_diagonal == 3:
                self.player1_count += 1
            if right_diagonal == 3:
                self.player1_count += 1
        else:
            if row == 3:
                self.player2_count += 1
            if col == 3:
                self.player2_count += 1
            if left_diagonal == 3:
                self.player2_count += 1
            if right_diagonal == 3:
                self.player2_count += 1

        return False

    # 가로줄 확인
    def check_row(self, cur_x, cur_y, player):
        return self.check_left(cur_x, cur_y, player) + self.check_right(cur_x, cur_y, player) + 1

    def check_left(self, cur_x, cur_y, player):
        if cur_x != 0 and self.map[cur_y][cur_x - 1] == player:
            return self.check_left(cur_x - 1, cur_y, player) + 1
        return 0

    def check_right(self, cur_x, cur_y, player):
        if cur_x != 7 and self.map[cur_y][cur_x + 1] == player:
            return self.check_right(cur_x + 1, cur_y, player) + 1
        return 0

    # 세로줄 확인
    def check_col(self, cur_x, cur_y, player):
        return self.check_bottom(cur_x, cur_y, player) + self.check_top(cur_x, cur_y, player) + 1

    def check_bottom(self, cur_x, cur_y, player):
        if cur_y != 0 and self.map[cur_y - 1][cur_x] == player:
            return self.check_bottom(cur_x, cur_y - 1, player) + 1
        return 0

    def check_top(self, cur_x, cur_y, player):
        if cur_y != 7 and self.map[cur_y + 1][cur_x] == player:
            return self.check_top(cur_x, cur_y + 1, player) + 1
        return 0

    # 왼쪽 대각선 확인 (\)
    def check_left_diagonal(self, cur_x, cur_y, player):
        return self.check_left_diagonal_top(cur_x, cur_y, player) + self.check_left_diagonal_bottom(cur_x, cur_y, player) + 1

    def check_left_diagonal_top(self, cur_x, cur_y, player):
        if cur_x != 0 and cur_y != 0 and self.map[cur_y - 1][cur_x - 1] == player:
            return self.check_left_diagonal_top(cur_x - 1, cur_y - 1, player) + 1
        return 0

    def check_left_diagonal_bottom(self, cur_x, cur_y, player):
        if cur_x != 7 and cur_y != 7 and self.map[cur_y + 1][cur_x + 1] == player:
            return self.check_left_diagonal_bottom(cur_x + 1, cur_y + 1, player) + 1
        return 0

    # 오른쪽 대각선 확인 (/)
    def check_right_diagonal(self, cur_x, cur_y, player):
        return self.check_right_diagonal_top(cur_x, cur_y, player) + self.check_right_diagonal_bottom(cur_x, cur_y, player) + 1

    def check_right_diagonal_top(self, cur_x, cur_y, player):
        if cur_x != 7 and cur_y != 0 and self.map[cur_y - 1][cur_x + 1] == player:
            return self.check_right_diagonal_top(cur_x + 1, cur_y - 1, player) + 1
        return 0

    def check_right_diagonal_bottom(self, cur_x, cur_y, player):
        if cur_x != 0 and cur_y != 7 and self.map[cur_y + 1][cur_x - 1] == player:
            return self.check_right_diagonal_bottom(cur_x - 1, cur_y + 1, player) + 1
        return 0

    # 무승부시 플레이어1이 3개가 이어진게 많으면 1 리턴 플레이어2가 더 많으면 2리턴, 무승부면 3리턴
    def get_tie_winner(self):
        if self.player1_count > self.player2_count:
            return 1
        elif self.player1_count < self.player2_count:
            return 2
        return 3

    #3개 리워드 확인
    def reward_cul(self, player):
        row_point = self.check_rows(self.x_point, self.y_point, player)
        col_point = self.check_cols(self.x_point, self.y_point, player)
        left_diagonal_point = self.check_left_diagonals(self.x_point, self.y_point, player)
        right_diagonal_point = self.check_right_diagonals(self.x_point, self.y_point, player)

        return row_point + col_point + left_diagonal_point + right_diagonal_point + 1.0

    # 가로줄 확인
    def check_rows(self, cur_x, cur_y, player):
        return self.check_lefts(cur_x, cur_y, player) + self.check_rights(cur_x, cur_y, player)

    def check_lefts(self, cur_x, cur_y, player):
        re = []
        if cur_x == 7:
            re.append(2)
        else:
            if self.map[cur_y][cur_x + 1] == player:
                re.append(1)
            elif self.map[cur_y][cur_x + 1] == 0:
                re.append(0)
            else:
                re.append(2)
        re.append(1)

        for i in range(3):
            if cur_x - (i+1) >= 0:
                re = [2, 1]
                if self.map[cur_y][cur_x - (i+1)] == player:
                    re.append(1)
                elif self.map[cur_y][cur_x - (i+1)] == 0:
                    re.append(0)
                else:
                    re.append(2)
            else:
                re.append(2)
        return self.reward_point_check(re)

    def check_rights(self, cur_x, cur_y, player):
        re = []
        if cur_x == 0:
            re.append(2)
        else:
            if self.map[cur_y][cur_x - 1] == player:
                re.append(1)
            elif self.map[cur_y][cur_x - 1] == 0:
                re.append(0)
            else:
                re.append(2)
        re.append(1)

        for i in range(3):
            if cur_x + i+1 <= 7:
                if self.map[cur_y][cur_x + i+1] == player:
                    re.append(1)
                elif self.map[cur_y][cur_x + i+1] == 0:
                    re.append(0)
                else:
                    re.append(2)
            else:
                re.append(2)
        return self.reward_point_check(re)

    # 세로줄 확인
    def check_cols(self, cur_x, cur_y, player):
        return self.check_bottoms(cur_x, cur_y, player) + self.check_tops(cur_x, cur_y, player)

    def check_bottoms(self, cur_x, cur_y, player):
        re = []
        if cur_y == 0:
            re.append(2)
        else:
            if self.map[cur_y - 1][cur_x] == player:
                re.append(1)
            elif self.map[cur_y - 1][cur_x] == 0:
                re.append(0)
            else:
                re.append(2)
        re.append(1)

        for i in range(3):
            if cur_y + i + 1 <= 7:
                if self.map[cur_y + i + 1][cur_x] == player:
                    re.append(1)
                elif self.map[cur_y + i+1][cur_x] == 0:
                    re.append(0)
                else:
                    re.append(2)
            else:
                re.append(2)
        return self.reward_point_check(re)

    def check_tops(self, cur_x, cur_y, player):
        re = []
        if cur_y == 7:
            re.append(2)
        else:
            if self.map[cur_y + 1][cur_x] == player:
                re.append(1)
            elif self.map[cur_y + 1][cur_x] == 0:
                re.append(0)
            else:
                re.append(2)
        re.append(1)

        for i in range(3):
            if cur_y - (i + 1) >= 0:
                if self.map[cur_y - (i+1)][cur_x] == player:
                    re.append(1)
                elif self.map[cur_y - (i+1)][cur_x] == 0:
                    re.append(0)
                else:
                    re.append(2)
            else:
                re.append(2)
        return self.reward_point_check(re)

    # 왼쪽 대각선 확인 (\)
    def check_left_diagonals(self, cur_x, cur_y, player):
        return self.check_left_diagonal_tops(cur_x, cur_y, player) + self.check_left_diagonal_bottoms(cur_x, cur_y, player)

    def check_left_diagonal_tops(self, cur_x, cur_y, player):
        re = []
        if cur_x == 7 or cur_y == 7:
            re.append(2)
        else:
            if self.map[cur_y + 1][cur_x + 1] == player:
                re.append(1)
            elif self.map[cur_y + 1][cur_x + 1] == 0:
                re.append(0)
            else:
                re.append(2)
        re.append(1)

        for i in range(3):
            if cur_x - (i+1) >= 0 and cur_y - (i+1) >= 0:
                if self.map[cur_y - (i+1)][cur_x - (i+1)] == player:
                    re.append(1)
                elif self.map[cur_y - (i+1)][cur_x - (i+1)] == 0:
                    re.append(0)
                else:
                    re.append(2)
            else:
                re.append(2)
            return self.reward_point_check(re)

    def check_left_diagonal_bottoms(self, cur_x, cur_y, player):
        re = []
        if cur_x == 0 or cur_y == 0:
            re.append(2)
        else:
            if self.map[cur_y - 1][cur_x - 1] == player:
                re.append(1)
            elif self.map[cur_y - 1][cur_x - 1] == 0:
                re.append(0)
            else:
                re.append(2)
        re.append(1)

        for i in range(3):
            if cur_x + i + 1 <= 7 and cur_y + i + 1 <= 7:
                if self.map[cur_y + i+1][cur_x + i+1] == player:
                    re.append(1)
                elif self.map[cur_y + i+1][cur_x + i+1] == 0:
                    re.append(0)
                else:
                    re.append(2)
            else:
                re.append(2)
        return self.reward_point_check(re)

    # 오른쪽 대각선 확인 (/)
    def check_right_diagonals(self, cur_x, cur_y, player):
        return self.check_right_diagonal_tops(cur_x, cur_y, player) + self.check_right_diagonal_bottoms(cur_x, cur_y, player)

    def check_right_diagonal_tops(self, cur_x, cur_y, player):
        re = []
        if cur_x == 7 or cur_y == 0:
            re.append(2)
        else:
            if self.map[cur_y - 1][cur_x + 1] == player:
                re.append(1)
            elif self.map[cur_y - 1][cur_x + 1] == 0:
                re.append(0)
            else:
                re.append(2)
        re.append(1)

        for i in range(3):
            if cur_x + i+1 <= 7 and cur_y - (i+1) >= 0:
                if self.map[cur_y - (i+1)][cur_x + (i+1)] == player:
                    re.append(1)
                elif self.map[cur_y - (i+1)][cur_x + (i+1)] == 0:
                    re.append(0)
                else:
                    re.append(2)
            else:
                re.append(2)
        return self.reward_point_check(re)

    def check_right_diagonal_bottoms(self, cur_x, cur_y, player):
        re = []
        if cur_x == 0 or cur_y == 7:
            re.append(2)
        else:
            if self.map[cur_y + 1][cur_x - 1] == player:
                re.append(1)
            elif self.map[cur_y + 1][cur_x - 1] == 0:
                re.append(0)
            else:
                re.append(2)
        re.append(1)

        for i in range(3):
            if cur_x - (i+1) >= 0 and cur_y + i+1 <= 7:
                if self.map[cur_y + (i+1)][cur_x - (i+1)] == player:
                    re.append(1)
                elif self.map[cur_y + (i+1)][cur_x - (i+1)] == 0:
                    re.append(0)
                else:
                    re.append(2)
            else:
                re.append(2)
        return self.reward_point_check(re)

    def reward_point_check(self, re):
        reward = 0.0
        if re in self.reward_point_1:
            reward += 1.0
        if self.reward_cul_check and re in self.reward_point_2:
            reward += 1.0
            self.reward_cul_check = False
        return reward