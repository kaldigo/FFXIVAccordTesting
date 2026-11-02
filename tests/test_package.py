import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('package', Path(__file__).resolve().parents[1] / 'tools/package.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)

class ChannelIsolation(unittest.TestCase):
    def manifest(self, name='AccordRSRTesting'):
        return dict(InternalName=name, AssemblyVersion='0.1.0.0', DalamudApiLevel=15,
                    RepoUrl='https://github.com/' + package.REPOSITORIES.get(name, 'kaldigo/FFXIVAccord'))

    def test_independent_pair_is_accepted(self):
        for name in package.REPOSITORIES:
            package.validate_manifest(self.manifest(name), name, '0.1.0.0')

    def test_stable_identities_cannot_be_published_here(self):
        for name in ['Accord', 'WrathCombo', 'RotationSolver']:
            with self.assertRaises(ValueError): package.validate_manifest(self.manifest(name), name, '0.1.0.0')

    def test_testing_version_cannot_replace_stable_channel(self):
        manifest = self.manifest()
        manifest['TestingAssemblyVersion'] = '0.2.15.99'
        with self.assertRaises(ValueError): package.validate_manifest(manifest, 'AccordRSRTesting', '0.1.0.0')

    def test_wrong_version_and_repository_are_rejected(self):
        for key, value in [('AssemblyVersion', '0.2.0.0'), ('RepoUrl', 'https://github.com/kaldigo/FFXIVAccord'), ('DalamudApiLevel', 14)]:
            manifest = self.manifest()
            manifest[key] = value
            with self.assertRaises(ValueError): package.validate_manifest(manifest, 'AccordRSRTesting', '0.1.0.0')

if __name__ == '__main__': unittest.main()
