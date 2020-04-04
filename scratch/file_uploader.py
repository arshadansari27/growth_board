from notion_api import NotionDB

TOKEN = "76c45addb4795e4e324231c33610975e4aadf213f43b062bac51316343bfc7001e17053c3c65e87bc4375b9a525f9cd4f544cf9b1dc7b5cadcf534851e03105b4ffed4e936726b948d4d5048c405"
#1812e4316f612e3740c5686bc75bd2e3057c1722f88099f755ed4a3b79b64bcd11ea5c720cc263da7ace59300868947cf84d480c62af42d233e13f0a6c13127836b8f58427d8539e3f50483cf291
URL = "https://www.notion.so/a2c28de35349469caedf8cbc78ef4404?v=f55491f003c14d0b9d7ff6f5ede4ccac"
file_path = '/Users/arshad/Desktop/Gaurav_resume.pdf'

db = NotionDB(URL, token=TOKEN)
title = 'File Upload Example'
field = 'Files'
with open(file_path, 'rb') as data:
    db.upload_file(title, field, 'application/pdf',
               'Gaurav_resume.pdf', data)
row = db.get_or_create(title)
print(row.title, row.Files)
