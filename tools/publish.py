"""Manual future-client publication; deliberately refuses the empty workspace."""
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from workspace import ROOT, config

def publish(version):
    cfg = config(require_project=True)
    if not re.fullmatch(r'\d+\.\d+\.\d+\.\d+', version):
        raise ValueError('Use a new four-part version')
    out = ROOT / 'artifacts'
    build = out / 'build'
    name = cfg['internal_name']
    subprocess.run(['dotnet','build',str(ROOT / cfg['project']),'-c','Release',f'-p:Version={version}','--output',str(build)], check=True)
    manifest = json.loads((build / (name + '.json')).read_text(encoding='utf-8-sig'))
    if manifest.get('InternalName') != name or manifest.get('AssemblyVersion') != version:
        raise ValueError('Built plugin identity or version differs from the release plan')
    if any(k.startswith('Testing') for k in manifest):
        raise ValueError('Use the separate plugin identity, not stable Accord testing-version fields')
    url = f'https://github.com/{cfg["repository"]}/releases/download/v{version}/{name}.zip'
    manifest.update(RepoUrl='https://github.com/' + cfg['repository'], DownloadLinkInstall=url, DownloadLinkUpdate=url, DownloadLinkTesting=url)
    archive = out / (name + '.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for path in build.rglob('*'):
            if not path.is_file(): continue
            if path.name in ('Accord.dll', 'AccordRSREngine.dll', 'WrathCombo.dll', 'RotationSolver.dll'):
                raise ValueError('Unrelated engine or stable binary in client output')
            if path.suffix == '.dll' or path.name.endswith('.deps.json'):
                z.write(path, path.relative_to(build).as_posix())
        if name + '.dll' not in z.namelist(): raise ValueError('Missing client assembly')
        z.writestr(name + '.json',json.dumps(manifest,indent=2))
        z.write(ROOT / 'LICENSE','LICENSE')
    feed = out / 'pluginmaster.json'
    feed.write_text(json.dumps([manifest],indent=2)+'\n',encoding='utf-8')
    sums = out / 'SHA256SUMS.txt'
    sums.write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
    # gh release create refuses an existing release; do not clobber published assets.
    subprocess.run(['gh','release','create','v'+version,str(archive),str(feed),str(sums),'--repo',cfg['repository'],'--target',subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'--prerelease','--title','Accord Testing '+version,'--notes','Independent testing preview. Native validation status must be reviewed before use.'],check=True)
    (ROOT / 'pluginmaster.json').write_bytes(feed.read_bytes())

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--version',required=True)
    publish(p.parse_args().version)
