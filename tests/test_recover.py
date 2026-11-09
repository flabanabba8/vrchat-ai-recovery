import contextlib
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import recover


def bundle(payload=b'example'):
    version = struct.pack('>I', 7)
    strings = b'5.x.x\0test-engine\0'
    size = 8 + 4 + len(strings) + 20 + len(payload)
    return b'UnityFS\0' + version + strings + struct.pack('>QIII', size, 1, 1, 0) + payload


def glb(document, binary=b''):
    document = {'asset': {'version': '2.0'}, **document}
    raw = json.dumps(document, separators=(',', ':')).encode()
    raw += b' ' * (-len(raw) % 4)
    chunks = struct.pack('<II', len(raw), 0x4E4F534A) + raw
    if binary:
        binary += b'\0' * (-len(binary) % 4)
        chunks += struct.pack('<II', len(binary), 0x004E4942) + binary
    return struct.pack('<III', 0x46546C67, 2, 12 + len(chunks)) + chunks


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def file(self, data, name='input.bin'):
        target = self.root / name
        target.write_bytes(data)
        return target

    def test_bundle_carving_stream_boundary_and_hash(self):
        first, second = bundle(b'first'), bundle(b'second')
        source = self.file(b'x' * 13 + first + b'xx' + second)
        with patch.object(recover, 'CHUNK', 16):
            report = recover.carve(source, self.root / 'out')
        self.assertEqual([r['offset'] for r in report['bundles']], [13, 13 + len(first) + 2])
        import hashlib
        for record, expected in zip(report['bundles'], [first, second]):
            self.assertEqual((self.root / 'out' / record['file']).read_bytes(), expected)
            self.assertEqual(record['sha256'], hashlib.sha256(expected).hexdigest())
        self.assertEqual(source.read_bytes(), b'x' * 13 + first + b'xx' + second)

    def test_truncated_bundle_does_not_create_output(self):
        source = self.file(bundle()[:-2])
        with self.assertRaises(ValueError):
            recover.carve(source, self.root / 'out')
        self.assertFalse((self.root / 'out').exists())

    def test_output_is_never_overwritten(self):
        source = self.file(bundle())
        output = self.root / 'out'
        output.mkdir()
        marker = output / 'keep'
        marker.write_text('keep')
        with self.assertRaises(FileExistsError):
            recover.carve(source, output)
        self.assertEqual(marker.read_text(), 'keep')

    def test_rejects_source_symlink(self):
        source = self.file(bundle())
        link = self.root / 'link'
        link.symlink_to(source)
        with self.assertRaises(ValueError):
            recover.carve(link, self.root / 'out')

    def test_malformed_header_and_false_signature(self):
        source = self.file(b'UnityFS\0' + b'\0' * 250 + bundle()[:18])
        self.assertEqual(list(recover.find_bundles(source)), [])

    def test_glb_counts_do_not_duplicate_shared_positions(self):
        primitive = {'attributes': {'POSITION': 0}, 'targets': [{'POSITION': 0}]}
        document = {'accessors': [{'count': 3}], 'meshes': [{'primitives': [primitive, primitive]}],
                    'skins': [{'joints': [0, 1]}], 'nodes': [{}, {}],
                    'animations': [{'channels': [{'target': {'path': 'pointer'}}]}]}
        report = recover.inspect_glb(self.file(glb(document)))
        self.assertEqual(report['unique_position_accessor_vertices'], 3)
        self.assertEqual(report['primitives'], 2)
        self.assertEqual(report['skin_joint_counts'], [2])
        self.assertEqual(report['morph_target_counts_per_mesh'], [[1]])
        self.assertEqual(report['material_pointer_channels'], 1)

    def test_invalid_position_count_is_rejected(self):
        document = {'accessors': [{'count': -1}], 'meshes': [{'primitives': [{'attributes': {'POSITION': 0}}]}]}
        with self.assertRaisesRegex(ValueError, 'count'):
            recover.inspect_glb(self.file(glb(document)))

    def test_glb_embedded_buffer_range(self):
        valid = {'buffers': [{'byteLength': 4}], 'bufferViews': [{'buffer': 0, 'byteLength': 4}]}
        self.assertEqual(recover.inspect_glb(self.file(glb(valid, b'1234')))['format'], 'GLB2')
        valid['bufferViews'][0]['byteOffset'] = 1
        with self.assertRaisesRegex(ValueError, 'outside'):
            recover.inspect_glb(self.file(glb(valid, b'1234')))

    def test_glb_rejects_incorrect_file_length(self):
        with self.assertRaises(ValueError):
            recover.inspect_glb(self.file(glb({}) + b'x'))

    def test_glb_rejects_truncated_chunk(self):
        raw = bytearray(glb({}))
        struct.pack_into('<I', raw, 12, len(raw))
        with self.assertRaises(ValueError):
            recover.inspect_glb(self.file(raw))

    def test_external_files_are_only_flagged_not_opened(self):
        report = recover.inspect_glb(self.file(glb({'buffers': [{'byteLength': 4, 'uri': 'not-a-real-file'}]})))
        self.assertTrue(report['external_uris_present'])
        self.assertNotIn('not-a-real-file', json.dumps(report))

    def test_brief_omits_embedded_names_and_paths(self):
        report = recover.inspect_glb(self.file(glb({'nodes': [{'name': 'untrusted-input-string'}],
                                                  'extras': {'source': 'another-private-string'}})))
        brief = recover.ai_plan(report)
        self.assertNotIn('untrusted-input-string', brief)
        self.assertNotIn('another-private-string', brief)
        self.assertIn('untrusted data', brief)

    def test_cli_failure_omits_local_path(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = recover.main(['inspect', str(self.root / 'missing')])
        self.assertEqual(code, 1)
        self.assertNotIn(str(self.root), stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
