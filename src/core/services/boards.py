from core.models import Board, Iternary
from core.services import Context, ServiceMixin


class BoardService(ServiceMixin[Board]):

    def __init__(self, context: Context):
        super(BoardService, self).__init__(context, Board)

    @property
    def repo(self):
        return self.context.board_repo

    def add_iternary_to_map(
            self,
            board: Board,
            iternary: Iternary,
            after: Iternary,
            before: Iternary):
        board.add(iternary, after=after, before=before)
        return self.repo.create_update(board)

    def remove_iternary_from_map(self, board: Board, iternary: Iternary):
        board.remove(iternary)
        return self.repo.create_update(board)

