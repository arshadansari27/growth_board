import os
from pathlib import Path

from growth.integration import NotionDB

url = 'https://www.notion.so/02498fb7596c45999e5b2619608a8c04?v=849b990573454c0d9824c005fb2853ff'
path = Path('/Users/arshad/Dropbox/calibre').absolute()

db = NotionDB(url)


def is_ds_store(path):
    if str(path).endswith('.DS_Store'):
        return True
    return False

books = []
for author in os.listdir(path):
    author_path = path / author
    if not author_path.is_dir() or is_ds_store(author_path):
        continue
    for book in os.listdir(author_path):
        book_path = path / author / book
        if not author_path.is_dir() or is_ds_store(book_path):
            continue
        cover = book_path / 'cover.jpg'
        cover.exists()
        book_formats = []
        for file in os.listdir(book_path):
            format_path = book_path / file
            if file in {'cover.jpg', 'metadata.opf', '.DS_Store'}:
                continue
            book_formats.append(Path(author) / book / file)
        books.append((author, book, cover, book_formats))

for book in books:
    name = ' '.join(book[1].split(' ')[:-1])
    author = book[0]
    cover = book[2]
    files = book[3]
    node = db.get_or_create(name)
    if node.author != author:
        node.author = author
    if not node.files:
        node.files = [str(u) for u in files]
    node.location = 'Calibre'
