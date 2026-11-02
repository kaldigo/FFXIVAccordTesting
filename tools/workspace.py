"""Validate the empty workspace and guard the future independent publish flow."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def config(require_project=False):
    value = json.loads((ROOT / 'release-config.json').read_text(encoding='utf-8-sig'))
    if value.get('repository') != 'kaldigo/FFXIVAccordTesting' or value.get('internal_name') != 'AccordRSRTesting':
        raise ValueError('Publishing must use the independent testing repository and identity')
    project = value.get('project')
    if project:
        path = (ROOT / project).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or path.suffix != '.csproj':
            raise ValueError('Project must be an implemented csproj inside this repository')
    elif require_project:
        raise ValueError('No plugin is implemented. Nothing can be built or published yet.')
    return value

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--require-project', action='store_true')
    args = p.parse_args()
    config(args.require_project)
    print('Independent testing workspace valid.')
