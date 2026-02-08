import datetime
import json
import pathlib
import re

BASE_DIR = pathlib.Path(__file__).resolve().parent
BIB_PATH = BASE_DIR / 'refs.bib'
MAP_PATH = BASE_DIR / '_refs_validation_map.json'
OUT_PATH = BASE_DIR / 'REFS_VALIDATION.md'

text = BIB_PATH.read_text(encoding='utf-8')
entries: dict[str, str] = {}
cur_key = None
cur_lines: list[str] = []

for line in text.splitlines():
    match = re.match(r'^@\w+\s*\{\s*([^,]+)\s*,', line)
    if match:
        if cur_key:
            entries[cur_key] = '\n'.join(cur_lines).strip()
        cur_key = match.group(1).strip()
        cur_lines = [line]
    elif cur_key:
        cur_lines.append(line)

if cur_key:
    entries[cur_key] = '\n'.join(cur_lines).strip()

ref_map = {item['key']: item for item in json.loads(MAP_PATH.read_text(encoding='utf-8'))}

lines: list[str] = []
lines.append('# References Validation')
lines.append('')
lines.append(f'Date: {datetime.date.today().isoformat()}')
lines.append('')

for key in sorted(entries.keys()):
    meta = ref_map.get(key, {})
    status = meta.get('status', 'NOT_FOUND')
    doi = meta.get('doi')
    doi_url = meta.get('doi_url')
    primary_url = meta.get('primary_url')

    lines.append(f'## {key}')
    lines.append(f'Status: {status}')
    if doi:
        lines.append(f'DOI: {doi}')
    if doi_url:
        lines.append(f'DOI URL: {doi_url}')
    if primary_url:
        lines.append(f'Primary URL: {primary_url}')
    if status != 'FOUND':
        lines.append('Note: No Crossref match found; manual verification required.')
    lines.append('')
    lines.append('BibTeX:')
    lines.append('```bibtex')
    lines.append(entries[key])
    lines.append('```')
    lines.append('')

OUT_PATH.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
