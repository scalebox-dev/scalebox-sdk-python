#!/usr/bin/env python3
"""
Tests for ``GET /scalebox-regions`` via ``SandboxApi.get_regions`` / ``parse_scalebox_regions_response``.

- **Unit**: JSON parsing (no network).
- **Live** (optional): real API when ``SBX_API_KEY`` is set; skipped otherwise.

Run::

    PYTHONPATH=<repo-root> python3 -m unittest scalebox.test.test_sandbox_get_regions -v
"""

from __future__ import annotations

import asyncio
import os
import unittest

from scalebox.sandbox.sandbox_api import ScaleboxRegion, parse_scalebox_regions_response


class TestParseScaleboxRegionsResponse(unittest.TestCase):
    def test_happy_path(self) -> None:
        body = {
            "success": True,
            "data": {
                "scalebox_regions": [
                    {"id": "us-east", "name": "US East"},
                    {"id": "ap-southeast", "name": "AP Southeast"},
                ]
            },
        }
        out = parse_scalebox_regions_response(body)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0], ScaleboxRegion(id="us-east", name="US East"))
        self.assertEqual(out[1].id, "ap-southeast")
        self.assertEqual(out[1].name, "AP Southeast")

    def test_empty_list(self) -> None:
        body = {"success": True, "data": {"scalebox_regions": []}}
        self.assertEqual(parse_scalebox_regions_response(body), [])

    def test_missing_data_returns_empty(self) -> None:
        self.assertEqual(parse_scalebox_regions_response({"success": True}), [])
        self.assertEqual(parse_scalebox_regions_response({}), [])

    def test_missing_scalebox_regions_returns_empty(self) -> None:
        self.assertEqual(
            parse_scalebox_regions_response({"success": True, "data": {}}),
            [],
        )

    def test_non_dict_body_returns_empty(self) -> None:
        self.assertEqual(parse_scalebox_regions_response(None), [])
        self.assertEqual(parse_scalebox_regions_response([]), [])

    def test_skips_items_without_id(self) -> None:
        body = {
            "data": {
                "scalebox_regions": [
                    {"name": "No id"},
                    {"id": "keep-me", "name": "OK"},
                ]
            }
        }
        out = parse_scalebox_regions_response(body)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].id, "keep-me")

    def test_name_defaults_to_empty_string(self) -> None:
        body = {"data": {"scalebox_regions": [{"id": "x"}]}}
        out = parse_scalebox_regions_response(body)
        self.assertEqual(out[0].name, "")


class TestGetRegionsLive(unittest.TestCase):
    """Call Scalebox API; requires ``SBX_API_KEY`` unless skipped."""

    def test_sync_get_regions_live(self) -> None:
        if not os.getenv("SBX_API_KEY"):
            self.skipTest("SBX_API_KEY not set")
        from scalebox.sandbox_sync.main import Sandbox

        regions = Sandbox.get_regions()
        self.assertIsInstance(regions, list)
        for r in regions:
            self.assertIsInstance(r, ScaleboxRegion)
            self.assertTrue(r.id)

    def test_async_get_regions_live(self) -> None:
        if not os.getenv("SBX_API_KEY"):
            self.skipTest("SBX_API_KEY not set")
        from scalebox.sandbox_async.main import AsyncSandbox

        async def _run():
            return await AsyncSandbox.get_regions()

        regions = asyncio.run(_run())
        self.assertIsInstance(regions, list)
        for r in regions:
            self.assertIsInstance(r, ScaleboxRegion)
            self.assertTrue(r.id)


if __name__ == "__main__":
    unittest.main()
