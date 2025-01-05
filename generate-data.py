import asyncio
import json
import os
import sys
import urllib

import aiohttp
import dotenv
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

packages = []
for page in [1, 2, 3]:
    params.update(dict(page=page))
    response = requests.get('https://libraries.io/api/search', params=params)
    if response.status_code != 200:
        sys.exit(f'ERROR: libraries.io: {response.content}')
    else:
        packages += response.json()

with open('./data/packages.json', 'w') as fh:
    print(json.dumps(packages), file=fh)

with open('./data/packages.json') as fh:
    packages = json.load(fh)

print(len(packages))


async def fetch(session, project):
    url = f'https://pypi.org/pypi/{project}/json'
    try:
        async with session.get(url) as response:
            json_data = await response.json()
            with open(f'./data/json/{project}.json', 'w') as fh:
                print(json.dumps(json_data['info']['project_urls'], indent=2), file=fh)
    except Exception as e:
        raise Exception(project)


async def main():
    tasks = []
    async with aiohttp.ClientSession() as session:
        for pkg in packages:
            tasks.append(fetch(session, pkg['name']))

        await asyncio.gather(*tasks)


asyncio.run(main())


# based on https://github.com/pypi/warehouse/blob/main/warehouse/templates/packaging/detail.html
def normalize_label(label, url):
    if label.lower() in ['home', 'homepage', 'home page']:
        return 'homepage'
    if label.lower() in ['changelog', 'change log', 'changes', 'release notes', 'news', 'what\'s new', 'history']:
        return 'changelog'
    if label.lower().startswith(('docs', 'documentation')):
        return 'documentation'
    if label.lower().startswith(('bug', 'issue', 'tracker', 'report')):
        return 'issues'
    if label.lower().startswith(('funding', 'donate', 'donation', 'sponsor')):
        return 'funding'
    if urllib.parse.urlparse(url).netloc in ['readthedocs.io', 'readthedocs.org', 'rtfd.io', 'rtfd.org']:
        return 'documentation'
    if urllib.parse.urlparse(url).netloc.endswith(('.readthedocs.io', '.readthedocs.org', '.rtfd.io', '.rtfd.org')):
        return 'documentation'
    if urllib.parse.urlparse(url).netloc.startswith(('docs.', 'documentation.')):
        return 'documentation'
    if 'github' in urllib.parse.urlparse(url).netloc:
        return 'github'
    if 'gitlab' in urllib.parse.urlparse(url).netloc:
        return 'gitlab'
    if 'bitbucket' in urllib.parse.urlparse(url).netloc:
        return 'bitbucket'

    return 'other'


records = []
for pkg in packages:
    with open(f'./data/json/{pkg["name"]}.json', 'r') as fh:
        project_urls = json.load(fh)

    if project_urls is None:
        continue

    for (label, url) in project_urls.items():
        icon = normalize_label(label, url)
        records += [(pkg['name'], pkg['rank'], icon, label)]

df = pd.DataFrame.from_records(records, columns=['package', 'rank', 'item', 'label'])
df.sort_values(by=['rank', 'package'], ascending=[False, True], inplace=True)

print(df)

df.to_csv('./data/table.csv', index=False)
