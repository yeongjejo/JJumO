import numpy as np

from env import Env
from td3.td3 import TD3

def main():
    env = Env()

    player1 = TD3()
    player2 = TD3()

    for epi in range(10000000):
        for step in range(9):
            pass
    

if __name__ == '__main__':
    main()