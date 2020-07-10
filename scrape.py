import json
import requests
import lxml.html

url = 'https://rde.fandom.com/wiki/List_of_Police_Scanner_quotes_by_.awc'

resp = requests.get(url)
html = lxml.html.fromstring(resp.content)

ids = [el.attrib['id'] for el in html.cssselect('.mw-headline')]
tables = html.cssselect('table.toccolours')

groups = {}
for id, table in zip(ids, tables):
    quotes = []
    rows = table.cssselect('tr')[1:]
    for row in rows:
        cols = row.cssselect('td')
        hash = cols[0].text.strip()
        quote = cols[1].text_content().strip()
        if not hash: continue
        quotes.append({
            'hash': hash,
            'quote': quote
        })
    if quotes:
        groups[id] = quotes

with open('data/quotes.json', 'w') as f:
    json.dump(groups, f)