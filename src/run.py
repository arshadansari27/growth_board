from core.services import in_memory_context_factory
from core.services.boards import BoardService

if __name__ == '__main__':
    context = in_memory_context_factory()
    service = BoardService(context)
    e = service.new("name", "description")
    print(e.id, e.name, e.description)