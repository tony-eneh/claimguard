import json
import pathlib
import re
import urllib.parse

BASE_DIR = pathlib.Path(__file__).resolve().parent
BIB_PATH = BASE_DIR / 'refs.bib'
MAP_PATH = BASE_DIR / '_refs_validation_map.json'
OUT_PATH = BASE_DIR / '_refs_notfound_doi_urls.json'

text = BIB_PATH.read_text(encoding='utf-8')
entries = {}
cur_key = None
cur_lines = []

for line in text.splitlines():
    match = re.match(r'^@\w+\s*\{\s*([^,]+)\s*,', line)
    if match:
        if cur_key:
            entries[cur_key] = '\n'.join(cur_lines)
        cur_key = match.group(1).strip()
        cur_lines = [line]
    elif cur_key:
        cur_lines.append(line)
if cur_key:
    entries[cur_key] = '\n'.join(cur_lines)

ref_map = {item['key']: item for item in json.loads(MAP_PATH.read_text(encoding='utf-8'))}
not_found = [k for k, v in ref_map.items() if v.get('status') != 'FOUND']

out = []
for key in not_found:
    entry = entries.get(key, '')
    doi_match = re.search(r'\bdoi\s*=\s*[{\"]([^}\"]+)[}\"]', entry, re.IGNORECASE)
    doi = doi_match.group(1).strip() if doi_match else None
    if doi:
        doi_encoded = urllib.parse.quote(doi)
        url = f'https://api.crossref.org/works/{doi_encoded}?select=DOI,URL,resource,title'
        out.append({'key': key, 'doi': doi, 'url': url})

OUT_PATH.write_text(json.dumps(out, indent=2), encoding='utf-8')
