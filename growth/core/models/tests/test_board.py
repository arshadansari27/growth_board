import pytest

from growth.core.models.board import Board
from growth.core.models.objectives import Objective, Goal


def test_board_status_up_down():
    board = Board(1, 'test-board', 'desc')
    iternaries = [Goal(i, 'test-{i}') for i in range(5)]
    iternaries[2].add_next(iternaries[3])
    iternaries[3].add_next(iternaries[4])
    iternaries[2].add_previous(iternaries[1])
    iternaries[1].add_previous(iternaries[0])
    for i in iternaries:
        board.add(i)
    print(board.iterate())
    print(board.status_per_iternaries)
    for i in range(5):
        try:
            board.status_incr(iternaries[4])
            print(board.status_per_iternaries)
        except Exception as e:
            print(e)
    print('-' * 100)
    for i in range(5):
        board.status_decr(iternaries[4])
        print(board.status_per_iternaries)



