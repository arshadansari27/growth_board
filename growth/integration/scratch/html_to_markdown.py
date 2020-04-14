from io import StringIO

import pandas
import tomd
from bs4 import BeautifulSoup


def remove_attrs(elem):
    attrs  = [attr for attr in elem.attrs if attr != 'href']
    for attr in attrs:
        del elem[attr]
    return elem

def get_table_headers(table):
    """Given a table soup, returns all the headers"""
    headers = []
    for th in table.find("tr").find_all("th"):
        headers.append(th.text.strip())
    return headers

def get_table_rows(table):
    """Given a table, returns all its rows"""
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = []
        tds = tr.find_all("td")
        if len(tds) == 0:
            ths = tr.find_all("th")
            for th in ths:
                cells.append(th.text.strip())
        else:
            for td in tds:
                cells.append(td.text.strip())
        rows.append(cells)
    return rows

def get_table_as_pd(table):
    headers = get_table_headers(table)
    rows = get_table_rows(table)
    return pandas.DataFrame(rows, columns=headers)


def read_body(html):
    def prune_cdata(text):
        if text.startswith('<![CDATA['):
            return text.replace('<![CDATA[', '')[:-2].replace('`', "'")
        return text

    soup =  BeautifulSoup(html)
    for elem in soup.find_all():
        remove_attrs(elem)
    for macro in soup.find_all('ac:structured-macro'):
        if not macro:
            continue
        body_main = macro.find('ac:plain-text-body')
        if not body_main:
            continue
        body = prune_cdata(body_main.string)
        p = soup.new_tag('p')
        body = '\n'.join('`' + u + '`' for u in body.split('\n'))
        p.string = body
        macro.insert_after(p)
        macro.extract()

    for macro in soup.find_all('ac:link'):
        if not macro:
            continue
        body = prune_cdata(macro.string if macro.string else '')
        p = soup.new_tag('p')
        body = '\n'.join('`' + u + '`' for u in body.split('\n'))
        p.string = body
        macro.insert_after(p)
        macro.extract()
    for table in soup.find_all('table'):
        df = get_table_as_pd(table)
        data = StringIO()
        df.to_csv(data, sep='|')
        data.flush()
        data.seek(0)
        pre = soup.new_tag('p')
        pre.string = data.read()
        table.insert_after(pre)
        table.extract()

    data = tomd.Tomd(str(soup)).markdown
    return data.split('\n')
