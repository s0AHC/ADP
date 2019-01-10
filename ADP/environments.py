import sys

from typing import Dict, List, Tuple, Any
import random
from ADP.utilities import *
from itertools import chain  # for flattening the list efficiently
from pprint import pprint


class Maze(object):
    """Reading the path to the .txt file describing the Maze

    1 - wall
    0 - free
    G - goal
    T - trap
    S - start

    """

    def __init__(self):

        self.program_name = sys.argv[0]
        self.arguments = sys.argv[1:]
        self.count = len(self.arguments)

        if len(sys.argv) != 2:
            self.file_name = "/home/petar/test_maze.txt"
            #raise Exception("Need two arguments: arg1:=script_name  arg2:=path_to_the_file!")
        else:
            self.file_name = self.arguments[0]

        self.grid_world = []  # type: List[Any]
        self._actions = {
            0: 'up',
            1: 'down',
            2: 'left',
            3: 'right',
            4: 'idle'
        }
        self.state_num = None
        self.act_num = None
        self.shape = None  # type: Tuple[int, int]
        self.grid_actions = None  # type: (Dict[Tuple[int, int], List[str]])
        self.state_grid = None  # type: (List[Tuple[int, int]])
        self._current_state = None  # type: Tuple[int, int]
        self._P_g = {}
        self.cost = []
        self.col = 0
        self.row = 0
        self.start_state = 0

        self._open_world()
        self.print_grid()
        self._get_shape()
        self.start_pos()
        self._allowed_actions()
        #self.probability_transitions()

    def _open_world(self):
        with open(self.file_name, "r") as f:
            for ln in f:
                ln = ln.strip()
                if not ln.startswith("#"):
                    ln = ln.split()
                    self.grid_world.append(ln)

    def get_file_path(self):
        return self.file_name

    def set_file_path(self, new_path):
        self.file_name = new_path

    def start_pos(self):
        for r in range(self.row):
            for c in range(self.col):
                if self.grid_world[r][c] == 'S':
                    self.current_state = r, c
                    return r, c

    @property
    def num_states(self):
        self.state_num = len(self.state_grid)
        return self.state_num

    @property
    def num_actions(self):
        self.act_num = len(self.actions)
        return self.act_num

    def print_grid(self):
        print('\n'.join(map(' '.join, self.grid_world)))

    def _get_shape(self):
        self.col = len(self.grid_world[0])
        self.row = len(self.grid_world)
        self.shape = self.row, self.col
        return self.shape  # returns a tuple just as np.shape for np arrays

    def _allowed_actions(self):
        """looking at 'S's and '0's """
        self.grid_actions, self.state_grid = admissible_act(self.row, self.col, self.grid_world)

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, state_tuple):
        self._current_state = state_tuple

    def next_state(self, state, action):
        """
        :param action: the action to take in the environment
        :type action: string

        :param state: the position of the agent in the maze (row, col)
        :type state: tuple
        """

        i = 0
        j = 0
        acts = self.grid_actions[state]
        if action in acts:
            if action == 'up':
                i = -1
            elif action == 'down':
                i = +1
            elif action == 'left':
                j = -1
            elif action == 'right':
                j = 1
            elif action == 'idle':
                pass
        else:
            pass
            # print "No move made"
        return modify_state(state, i, j)

    def subs2action(self, subs):
        return self.grid_actions[self.subs2idx(subs)]

    def subs2idx(self, subs):
        return self.state_grid[subs]

    def idx2subs(self, idx):
        return self.state_grid.index(idx)


    @property
    def actions(self):
        return self._actions

    @actions.setter
    def actions(self, act):
        self._actions = act

    def back2start(self):
        self.current_state = self.start_pos()

    def action_execution(self, action, p=0.1):

        next_state = self.next_state(self.current_state, action)
        action_available = self.grid_actions[next_state]
        if action == 'up' or action == 'down':
            if 'left' in action_available and 'right' in action_available:
                if random.random() < (1 - 2 * p):
                    self.current_state = next_state
                else:
                    if random.choice([True, False]):
                        # go diagonally left
                        self.current_state = self.next_state(next_state, 'left')
                    else:
                        # go diagonally right
                        self.current_state = self.next_state(next_state, 'right')
            else:
                if 'left' in action_available:
                    if random.random() < (1 - 1 * p):
                        self.current_state = next_state
                    else:
                        self.current_state = self.next_state(next_state, 'left')
                elif 'right' in action_available:
                    if random.random() < (1 - 1 * p):
                        self.current_state = next_state
                    else:
                        self.current_state = self.next_state(next_state, 'right')
                else:
                    self.current_state = next_state
        elif action == 'left' or action == 'right':
            if 'up' in action_available and 'down' in action_available:
                if random.random() < (1 - 2 * p):
                    self.current_state = next_state
                else:
                    if random.choice([True, False]):
                        # go diagonally left
                        self.current_state = self.next_state(next_state, 'up')
                    else:
                        # go diagonally right
                        self.current_state = self.next_state(next_state, 'down')
            else:
                if 'up' in action_available:
                    if random.random() < (1 - 1 * p):
                        self.current_state = next_state
                    else:
                        self.current_state = self.next_state(next_state, 'up')
                elif 'down' in action_available:
                    if random.random() < (1 - 1 * p):
                        self.current_state = next_state
                    else:
                        self.current_state = self.next_state(next_state, 'down')
                else:
                    self.current_state = next_state

    def rand_policy(self):
        """[S,A]"""
        policy = np.ones([self.num_states, self.num_actions]) / self.num_actions
        return policy

    @property
    def P_g(self):
        prob = 1
        # cur_state = self.next_state(self.subs2idx(s)
        # nxt_state = self.idx2subs(, self.actions[a])
        for s in range(self.num_states):
            #available_actions=self.subs2action(s)
            p = {}
            for a in range(self.num_actions): #len(available_actions)
                nxt_state_r, nxt_state_c = self.next_state(self.subs2idx(s), self.actions[a])
                nxt_state = self.idx2subs((nxt_state_r, nxt_state_c))
                if self.grid_world[nxt_state_r][nxt_state_c] == 'G':
                    cost = -1
                elif self.grid_world[nxt_state_r][nxt_state_c] == 'T':
                    cost = 50
                else:
                    cost = 0
                p[a] = [(prob, nxt_state, cost)]
            self._P_g[s] = p
        return self._P_g

    # # def visualisation(self):
    # #     return 0
    # #

