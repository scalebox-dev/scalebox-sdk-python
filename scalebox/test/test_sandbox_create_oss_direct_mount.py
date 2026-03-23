#!/usr/bin/env python3
"""
Unit tests for sandbox create body fields used by OSS direct mount (oss_quick_guide.md).

Covers:
- object_storage as a single dict (legacy) with optional endpoint
- object_storage as a list of mount specs
- s3fs_executable_path, object_storage_direct_mount, locality

These tests only assert JSON shape produced by ``NewSandbox.to_dict()``; no API calls.

Run::

    python3 -m unittest scalebox.test.test_sandbox_create_oss_direct_mount

Or with pytest (if installed)::

    pytest scalebox/test/test_sandbox_create_oss_direct_mount.py -v
"""

from __future__ import annotations

import unittest

from scalebox.api.client.models.new_sandbox import NewSandbox


def _minimal(**kwargs) -> NewSandbox:
    return NewSandbox(
        template_id="tpl-test",
        timeout=600,
        metadata={},
        env_vars={},
        secure=False,
        allow_internet_access=True,
        **kwargs,
    )


class TestNewSandboxOssDirectMountBody(unittest.TestCase):
    def test_single_object_storage_dict_with_endpoint(self) -> None:
        body = _minimal(
            object_storage={
                "uri": "s3://scalex-packages/test/",
                "mount_point": "/mnt/oss",
                "access_key": "<AK>",
                "secret_key": "<SK>",
                "region": "us-east-2",
                "endpoint": "",
            },
        )
        d = body.to_dict()
        self.assertEqual(d["template"], "tpl-test")
        ospec = d["object_storage"]
        self.assertIsInstance(ospec, dict)
        self.assertEqual(ospec["uri"], "s3://scalex-packages/test/")
        self.assertEqual(ospec["endpoint"], "")
        self.assertEqual(ospec["mount_point"], "/mnt/oss")

    def test_multi_object_storage_list(self) -> None:
        mounts = [
            {
                "uri": "s3://scalex-packages/test/",
                "mount_point": "/mnt/oss",
                "access_key": "<AK>",
                "secret_key": "<SK>",
                "region": "us-east-2",
                "endpoint": "",
            },
            {
                "uri": "s3://scalex-packages/test/ttttt/",
                "mount_point": "/mnt/oss-ttttt",
                "access_key": "<AK>",
                "secret_key": "<SK>",
                "region": "us-east-2",
                "endpoint": "",
            },
        ]
        d = _minimal(object_storage=mounts).to_dict()
        self.assertEqual(d["object_storage"], mounts)
        self.assertIsInstance(d["object_storage"], list)
        self.assertEqual(len(d["object_storage"]), 2)

    def test_direct_mount_flags_locality_and_empty_s3fs_path(self) -> None:
        d = _minimal(
            object_storage_direct_mount=True,
            s3fs_executable_path="",
            locality={"region": "ap-southeast", "force": False},
        ).to_dict()
        self.assertTrue(d["object_storage_direct_mount"])
        self.assertEqual(d["s3fs_executable_path"], "")
        self.assertEqual(
            d["locality"],
            {"region": "ap-southeast", "force": False},
        )

    def test_locality_auto_detect(self) -> None:
        d = _minimal(locality={"auto_detect": True}).to_dict()
        self.assertEqual(d["locality"], {"auto_detect": True})

    def test_omits_unset_optional_fields(self) -> None:
        """Optional OSS fields at UNSET must not appear in the payload."""
        d = _minimal().to_dict()
        self.assertNotIn("s3fs_executable_path", d)
        self.assertNotIn("object_storage_direct_mount", d)
        self.assertNotIn("locality", d)
        self.assertNotIn("object_storage", d)

    def test_from_dict_roundtrip_preserves_new_fields(self) -> None:
        src = {
            "template": "tpl-x",
            "timeout": 300,
            "object_storage": [
                {"uri": "s3://b/", "mount_point": "/mnt/a", "region": "r"}
            ],
            "object_storage_direct_mount": False,
            "s3fs_executable_path": "",
            "locality": {"region": "ap-southeast", "force": False},
        }
        parsed = NewSandbox.from_dict(src)
        back = parsed.to_dict()
        self.assertEqual(back["template"], "tpl-x")
        self.assertFalse(back["object_storage_direct_mount"])
        self.assertEqual(back["s3fs_executable_path"], "")
        self.assertEqual(back["locality"]["region"], "ap-southeast")


if __name__ == "__main__":
    unittest.main()
