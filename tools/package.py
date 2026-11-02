"""Package the isolated experiment pair without changing any stable feed."""
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

REPOSITORIES = {
    'AccordRSRTesting': 'kaldigo/FFXIVAccordTesting',
    'AccordRSREngine': 'kaldigo/RotationSolverReborn',
}

def validate_manifest(manifest, name, version):
    if name not in REPOSITORIES or manifest.get('InternalName') != name:
        raise ValueError('Experimental package identity differs from the isolated channel')
    if manifest.get('AssemblyVersion') != version or manifest.get('DalamudApiLevel') != 15:
        raise ValueError('Unexpected version or Dalamud API')
    if any(key.startswith('Testing') for key in manifest):
        raise ValueError('The experiment must not use a stable-plugin testing version')
    if manifest.get('RepoUrl') != 'https://github.com/' + REPOSITORIES[name]:
        raise ValueError('Unexpected source repository')

def package(root, engine, version):
    if not re.fullmatch(r'\d+\.\d+\.\d+\.\d+', version):
        raise ValueError('Use an immutable four-part version')
    pin = (root / 'engine-validation.ref').read_text().strip()
    actual = subprocess.check_output(['git', '-C', str(engine), 'rev-parse', 'HEAD'], text=True).strip()
    if not re.fullmatch(r'[0-9a-f]{40}', pin) or actual != pin:
        raise ValueError('Engine source differs from the reviewed commit')
    if subprocess.check_output(['git', '-C', str(engine), 'status', '--porcelain'], text=True).strip():
        raise ValueError('Commit engine changes before packaging')
    out = root / 'artifacts'
    out.mkdir(exist_ok=True)
    feed = []
    sums = []
    for name, build, dlls, source, notices in [
        ('AccordRSRTesting', root / 'AccordRSRTesting/bin/Release', ['AccordRSRTesting.dll'], root, ['LICENSE', 'README.md']),
        ('AccordRSREngine', engine / 'artifacts/build', ['AccordRSREngine.dll', 'ECommons.dll', 'RebornMaterial.dll'], engine, ['COPYING', 'COPYING.LESSER', 'ACCORD-EXPERIMENT.md', 'UPSTREAM.ref']),
    ]:
        manifest = json.loads((build / (name + '.json')).read_text(encoding='utf-8-sig'))
        validate_manifest(manifest, name, version)
        url = 'https://github.com/' + REPOSITORIES[name] + '/releases/download/v' + version + '/' + name + '.zip'
        manifest.update(DownloadLinkInstall=url, DownloadLinkUpdate=url, DownloadLinkTesting=url,
                        Changelog='Initial opt-in native RSR baseline and cached selector workbench. Native acceptance pending; redesigned intent execution is not implemented.')
        archive = out / (name + '.zip')
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for dll in dlls:
                z.write(build / dll, dll)
            deps = build / (name + '.deps.json')
            if deps.exists(): z.write(deps, deps.name)
            z.writestr(name + '.json', json.dumps(manifest, indent=2) + '\n')
            for notice in notices: z.write(source / notice, 'notices/' + notice)
            if name == 'AccordRSREngine':
                z.writestr('notices/SOURCE.txt', f'Corresponding fork source: https://github.com/{REPOSITORIES[name]}/tree/{pin}\nUpstream: FFXIV-CombatReborn/RotationSolverReborn\nRuntime dependencies: ECommons 3.2.1.26; RebornMaterial 7.5.7.5.\n')
                cache = Path.home() / '.nuget/packages'
                for dependency, depversion in [('ecommons','3.2.1.26'), ('rebornmaterial','7.5.7.5')]:
                    nupkg = cache / dependency / depversion / f'{dependency}.{depversion}.nupkg'
                    with zipfile.ZipFile(nupkg) as pkg:
                        for member in pkg.namelist():
                            if not member.endswith('/') and (re.search(r'(^|/)(license|licence|copying|notice)', member, re.I) or member.endswith('.nuspec')):
                                z.writestr('notices/' + dependency + '/' + member, pkg.read(member))
        with zipfile.ZipFile(archive) as z:
            if any(Path(n).name in ('Accord.dll','WrathCombo.dll','RotationSolver.dll') for n in z.namelist()):
                raise ValueError('Stable identity in experimental package')
            for dll in dlls:
                if dll not in z.namelist(): raise ValueError('Missing dependency: ' + dll)
            validate_manifest(json.loads(z.read(name + '.json')), name, version)
        sums.append(hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name)
        feed.append(manifest)
    (out / 'pluginmaster.json').write_text(json.dumps(feed, indent=2) + '\n', encoding='utf-8')
    (out / 'SHA256SUMS.txt').write_text('\n'.join(sums) + '\n', encoding='utf-8')
    print('Validated isolated packages and candidate feed:', out)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--engine-root', type=Path, required=True)
    p.add_argument('--version', required=True)
    a = p.parse_args()
    package(Path(__file__).resolve().parents[1], a.engine_root.resolve(), a.version)
