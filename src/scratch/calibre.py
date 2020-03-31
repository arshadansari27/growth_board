import requests
from bs4 import BeautifulSoup

COOKIE='''
_rails_session=xJE26zMK%2BK10u1%2Fh4xw9pITonl6JfGi3y6exiENY1zylTDhgZs6soUinZcW6xYipBTVGtx0a3wDyDONV%2FO%2B5rWctjbywGb5o5EAzc81z%2FAr5wQx4tst3Pbz0569BCIcJ2Y7rUZJqDWRH5170g7tl1Y24CW6pLwCZXeCTsk7qpIJKmSQx0cpjOwrevt2WVIhVdpHMjEZU6zzX74A6Tg4Zoy%2BWpTy5oBPkeW0A--RViOzSVYxGCO5upd--szE487WAq6KbYzQU5R9z%2BQ%3D%3D; connect:sess=eyJ1c2VySWQiOiIxNjQ0MTg4Ny02NjBkLTRhMzEtYjQ2Yy1jZjkwMWQ2OTZjNDcifQ==; connect:sess.sig=fIr1K8ETnPFrMKf4qrEqGqJepJU; amazon-pay-abtesting-new-widgets=true; amazon-pay-abtesting-apa-migration=true; remember_token=1|b66f1adfd40fe08d760aacfd8eb3cdb708c344a5fd0f78f33d99344af69e92983d1ea1b04e800e87ebd4ed533177ca1face4c25739c7a9bd97e478c7cdccc189; session=.eJw9j01rwkAQhv9KmbOHfOgl4EFZuyQwGzYkys5FkKaNk51LVLQr_vduCu1peJmH9-MJx8-pvwxQXKdbv4Dj-QOKJ7ydoABUzWh4z8ibjNRuiVn5IKHBSDVi2Aqpd473jGqTEjcesy6h1vtajXmtyxB_kWsGzCo2h4ZJ2dyEbkVsPPHXN3GZmGBz1LOvfTix91pHRm3FBZw9Bye7pTvsPUolru0Cik2MdmndGjZ6zh_vTso1vGL326WffgdACgv4V39z7Dpirx-_ak7z.XndBNA.EaohvnWeBjldy2hf2NCulCoCFzw
'''
cookies = {}
for l in COOKIE.split(";"):
    if not l.strip():
        continue
    p = [x for x in l.strip().split('=') if x]
    cookies[p[0]] = p[1]

response = requests.get('http://localhost:8083/page/1', cookies=cookies)
soup = BeautifulSoup(response.text)
count = 0
for book in soup.find_all("div", {"id": "books"}):
    title = book.find("p", {'class': 'title'})
    link = book.find('a').attrs['href']
    link = link if 'book' in link else None
    print(title, link)
    if link:
        response = requests.get('http://localhost:8083' + link, cookies=cookies)
        print('\t', [response.text])
    count += 1
print("[*]", count)

