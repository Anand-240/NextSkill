"""Phase H4: scan all git history for the local key value and real-looking api_key values,
and scan committed data, tests and reports for emails and Indian phone numbers.

The key is compared in code and never printed."""
import re
import subprocess
from pathlib import Path
from engine import ROOT
from scripts.scan_data import scan

API_KEY = re.compile(r'api_key["\']?\s*[:=]\s*["\']?([0-9a-fA-F]{20,})')

def local_keys():
    env = ROOT / '.env'
    values = [line.split('=', 1)[1].strip().strip('"\'') for line in env.read_text().splitlines() if '=' in line] if env.exists() else []
    return [v for v in values if len(v) >= 16]

def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout

def history_findings():
    keys, found, objects = local_keys(), 0, 0
    blobs = {line.split()[0] for line in git('rev-list', '--objects', '--all').splitlines() if line.strip() and len(line.split()) > 1}
    for blob in blobs:
        kind = git('cat-file', '-t', blob).strip()
        if kind != 'blob':
            continue
        objects += 1
        text = subprocess.run(['git', 'cat-file', 'blob', blob], cwd=ROOT, capture_output=True).stdout.decode('utf-8', 'ignore')
        if any(k in text for k in keys) or API_KEY.search(text):
            found += 1
    messages = git('log', '--all', '--format=%B')
    found += any(k in messages for k in keys)
    return objects, found

def contact_findings():
    from scripts.build_data import EMAIL, PHONE
    problems = []
    for base in ('demo_data', 'tests', 'reports', 'evaluation'):
        for path in (ROOT / base).rglob('*'):
            if path.is_file() and path.suffix in {'.json', '.md', '.csv', '.py'}:
                text = path.read_text(errors='ignore')
                text = re.sub(r'https?://\S+', '', text)
                if EMAIL.search(text) and not path.name.startswith('test_'):
                    problems.append(f'{path.relative_to(ROOT)} email-like text')
                if PHONE.search(text) and path.suffix in {'.json', '.csv', '.md'}:
                    problems.append(f'{path.relative_to(ROOT)} phone-like text')
    return problems

if __name__ == '__main__':
    objects, found = history_findings()
    files, response_problems = scan()
    contacts = contact_findings()
    print(f'History: {objects} blobs scanned, findings: {found}')
    print(f'Responses: {files} files scanned, findings: {len(response_problems)}')
    print(f'Contact patterns outside responses: {len(contacts)}')
    for line in response_problems + contacts:
        print(' ', line)
    raise SystemExit(bool(found or response_problems))
