#!/usr/bin/env python3
"""Unit tests for the Sway display layout controller."""

from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE_ROOT / "private_dot_local/bin/executable_display-layouts"
SPEC = importlib.util.spec_from_loader(
    "display_layouts", SourceFileLoader("display_layouts", str(SCRIPT))
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {SCRIPT}")
display_layouts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(display_layouts)


class DisplayLayoutsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.original_state = display_layouts.STATE_PATH
        self.original_lock = display_layouts.LOCK_PATH
        self.original_workspaces = display_layouts.NWG_WORKSPACES_PATH
        display_layouts.STATE_PATH = root / "display-layouts.json"
        display_layouts.LOCK_PATH = root / "display-layouts.lock"
        display_layouts.NWG_WORKSPACES_PATH = root / "workspaces"

    def tearDown(self) -> None:
        display_layouts.STATE_PATH = self.original_state
        display_layouts.LOCK_PATH = self.original_lock
        display_layouts.NWG_WORKSPACES_PATH = self.original_workspaces
        self.temp_dir.cleanup()

    def test_identity_prefers_description_with_serial(self) -> None:
        output = {
            "name": "DP-7",
            "make": "Acer Technologies",
            "model": "R271",
            "serial": "T60AA0012411",
        }
        self.assertEqual(
            display_layouts.output_identity(output),
            "description:Acer Technologies R271 T60AA0012411",
        )

    def test_identity_falls_back_to_connector_without_serial(self) -> None:
        output = {
            "name": "eDP-1",
            "make": "Sharp Corporation",
            "model": "0x1518",
            "serial": "Unknown",
        }
        self.assertEqual(
            display_layouts.output_identity(output),
            "connector:eDP-1:Sharp Corporation 0x1518",
        )

    def test_profile_match_requires_exact_monitor_set(self) -> None:
        state = {
            "version": 1,
            "profiles": {
                "dock": {"monitors": ["connector:eDP-1", "description:Dock 1"]}
            },
        }
        key, _ = display_layouts.find_profile(
            state, ["connector:eDP-1", "description:Dock 1"]
        )
        self.assertEqual(key, "dock")
        key, profile = display_layouts.find_profile(state, ["connector:eDP-1"])
        self.assertIsNone(key)
        self.assertIsNone(profile)

    def test_state_update_is_atomic_and_idempotent(self) -> None:
        def add_profile(state: dict) -> bool:
            state["profiles"]["mobile"] = {"monitors": ["connector:eDP-1"]}
            return True

        original_sync = display_layouts.sync_to_chezmoi
        display_layouts.sync_to_chezmoi = lambda: None
        try:
            self.assertTrue(display_layouts.update_state(add_profile))
        finally:
            display_layouts.sync_to_chezmoi = original_sync
        state = json.loads(display_layouts.STATE_PATH.read_text())
        self.assertEqual(state["profiles"]["mobile"]["monitors"], ["connector:eDP-1"])
        leftovers = list(display_layouts.STATE_PATH.parent.glob(".display-layouts.json.*"))
        self.assertEqual(leftovers, [])

    def test_nwg_workspace_parser_resolves_names_and_descriptions(self) -> None:
        display_layouts.NWG_WORKSPACES_PATH.write_text(
            "workspace 1 output DP-7\n"
            "workspace 2 output 'Dell Inc. DELL U3011 PH5NY1BH326L'\n"
        )
        outputs = [
            {
                "name": "DP-7",
                "make": "Acer",
                "model": "R271",
                "serial": "ABC",
            },
            {
                "name": "DP-8",
                "make": "Dell Inc.",
                "model": "DELL U3011",
                "serial": "PH5NY1BH326L",
            },
        ]
        self.assertEqual(
            display_layouts.parse_nwg_workspaces(outputs),
            {
                "1": "description:Acer R271 ABC",
                "2": "description:Dell Inc. DELL U3011 PH5NY1BH326L",
            },
        )

    def test_seed_profiles_assign_all_ten_workspaces(self) -> None:
        state = json.loads(
            (SOURCE_ROOT / "private_dot_config/sway/display-layouts.json").read_text()
        )
        display_layouts.validate_state(state)
        self.assertEqual(
            {profile["label"] for profile in state["profiles"].values()},
            {"Office", "Home", "Mobile"},
        )
        for profile in state["profiles"].values():
            self.assertEqual(set(profile["workspaces"]), set(display_layouts.WORKSPACE_NAMES))
            self.assertTrue(set(profile["workspaces"].values()) <= set(profile["monitors"]))

    def test_unknown_monitor_set_is_not_applied(self) -> None:
        display_layouts.STATE_PATH.write_text('{"version": 1, "profiles": {}}\n')
        output = {
            "name": "DP-1",
            "make": "Example",
            "model": "Panel",
            "serial": "123",
            "non_desktop": False,
        }
        original_outputs = display_layouts.connected_outputs
        original_command = display_layouts.sway_command
        display_layouts.connected_outputs = lambda: [output]
        display_layouts.sway_command = lambda _command: self.fail(
            "unknown monitor set issued a Sway command"
        )
        try:
            self.assertFalse(display_layouts.apply_profile())
        finally:
            display_layouts.connected_outputs = original_outputs
            display_layouts.sway_command = original_command

    def test_saved_profile_applies_output_and_workspace_rules(self) -> None:
        identity = "description:Example Panel 123"
        profile = {
            "label": "Test",
            "monitors": [identity],
            "outputs": [
                {
                    "identity": identity,
                    "enabled": True,
                    "mode": "1920x1080@60Hz",
                    "position": [10, 20],
                    "scale": 1.0,
                    "transform": "normal",
                    "scale_filter": "smart",
                    "adaptive_sync": False,
                    "dpms": True,
                }
            ],
            "workspaces": {name: identity for name in display_layouts.WORKSPACE_NAMES},
        }
        display_layouts.STATE_PATH.write_text(
            json.dumps({"version": 1, "profiles": {"test": profile}})
        )
        output = {
            "name": "DP-1",
            "make": "Example",
            "model": "Panel",
            "serial": "123",
            "active": True,
            "non_desktop": False,
        }
        commands: list[str] = []
        original_outputs = display_layouts.connected_outputs
        original_command = display_layouts.sway_command
        original_json = display_layouts.sway_json
        original_hook = display_layouts.run_output_hook
        original_sleep = display_layouts.time.sleep
        display_layouts.connected_outputs = lambda: [output]
        display_layouts.sway_command = commands.append
        display_layouts.sway_json = lambda _message_type: []
        display_layouts.run_output_hook = lambda: None
        display_layouts.time.sleep = lambda _seconds: None
        try:
            self.assertTrue(display_layouts.apply_profile())
        finally:
            display_layouts.connected_outputs = original_outputs
            display_layouts.sway_command = original_command
            display_layouts.sway_json = original_json
            display_layouts.run_output_hook = original_hook
            display_layouts.time.sleep = original_sleep
        self.assertIn(
            'output "DP-1" enable mode 1920x1080@60Hz pos 10 20 '
            "transform normal scale 1 scale_filter smart adaptive_sync off dpms on",
            commands,
        )
        self.assertEqual(
            len([command for command in commands if command.startswith("workspace ")]),
            10,
        )


if __name__ == "__main__":
    unittest.main()
