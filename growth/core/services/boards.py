from core.models import Iternary
from core.models.board import Board
from core.services import Context, ServiceMixin


class BoardService(ServiceMixin[Board]):

    def __init__(self, context: Context):
        super(BoardService, self).__init__(context, Board)

    @property
    def repo(self):
        return self.context.board_repo

    def add_iternary(
            self,
            board_id: int,
            iternary: Iternary):
        board = self.repo.get(board_id)
        board.add(iternary)
        return self.repo.create_update(board)

    def remove_iternary(self, board_id: int, iternary: Iternary):
        board = self.repo.get(board_id)
        board.remove(iternary)
        return self.repo.create_update(board)

    def list_sorted(self, board_id: int):
        board = self.repo.get(board_id)
        return board.iterate()
