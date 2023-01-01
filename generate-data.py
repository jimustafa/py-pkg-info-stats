import asyncio
import json
import os
import re
import sys

import aiohttp
import dotenv
import lxml.html
import pandas as pd
import requests


config = {
    **dotenv.dotenv_values('.env'),
    **os.environ,
}

params = dict(
    platforms='PyPI',
    sort='rank',
    order='desc',
    page=1,
    per_page=100,
    api_key=config['LIBRARIES_API_KEY'],
)

data = []
for page in [1, 2, 3]:
    params.update(dict(page=page))
    response = requests.get('https://libraries.io/api/search', params=params)
    if response.status_code != 200:
        sys.exit(f'ERROR: libraries.io: {response.content}')
    else:
        data += response.json()

with open('./data/packages.json', 'w') as fh:
    print(json.dumps(data), file=fh)

with open('./data/packages.json') as fh:
    data = json.load(fh)

print(len(data))


async def fetch(session, project):
    url = f'https://pypi.org/project/{project}'
    try:
        async with session.get(url) as response:
            text = await response.text()
            with open(f'./data/html/{project}.html', 'w') as fh:
                print(text, file=fh)
    except Exception as e:
        raise Exception(project)


async def main():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for item in data:
            tasks.append(fetch(session, item['name']))

        await asyncio.gather(*tasks)


asyncio.run(main())


records = []
for item in data:
    tree = lxml.html.parse(f'./data/html/{item["name"]}.html')

    project_links = tree.xpath('(//h3[text()="Project links"])[1]/../ul/li')

    labels = [link.xpath('a/text()')[1].strip() for link in project_links]
    icons = [link.xpath('a/i/@class')[0] for link in project_links]
    icons = [re.compile(r'fa[sb] fa-(?P<icon>.+)').match(icon).group('icon') for icon in icons]

    records += [(item['name'], item['rank'], icon, label) for (icon, label) in zip(icons, labels)]

df = pd.DataFrame.from_records(records, columns=['package', 'rank', 'item', 'label'])
df.sort_values(by=['rank', 'package'], ascending=[False, True], inplace=True)

print(df)

df.to_csv('./data/table.csv', index=False)
