"""Generate RELEASE_NOTES.md for a SkyDoom test build.

The notes follow the v0.1.1-beta release notes layout. Version-specific
content comes from:

  * CHANGELOG.md (repo root): the build's "Status:" line and its changes;
  * the build's own zip: README.md (controls, "how it works"),
    KNOWN_ISSUES.md (rough edges), SOURCE.md (source commit), and the zip
    and skydoomskse.dll SHA256 checksums.

The output is plain ASCII, so it renders the same however it is published.

Usage:
  python -I make_release_notes.py --zip <SkyDoom-vX.Y.Z-beta.zip>
      --changelog <CHANGELOG.md> --version vX.Y.Z-beta [--out <file>]
"""

import argparse
import hashlib
import re
import textwrap
import zipfile
from pathlib import Path

REPO_URL = "https://github.com/SkyrimAIDev/SkyDoom"
UPSTREAM_RELEASES = "https://github.com/Caffs/SkyDoom/releases"


def wrap(text, indent):
    """Wrap to 78 columns without breaking URLs or hyphenated words."""
    return textwrap.fill(text, 78, subsequent_indent=indent,
                         break_long_words=False, break_on_hyphens=False)


def sections(markdown):
    """Split markdown on '## ' headings: {title: body}."""
    result, title, lines = {}, None, []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if title is not None:
                result[title] = "\n".join(lines).strip()
            title, lines = line[3:].strip(), []
        elif title is not None:
            lines.append(line)
    if title is not None:
        result[title] = "\n".join(lines).strip()
    return result


def changelog_entry(text, version):
    """Return (status, changes, previous_version) for a changelog version."""
    headings = re.findall(r"^## (v\S+)", text, re.MULTILINE)
    if version not in headings:
        raise SystemExit(f"{version} not found in the changelog")
    body = sections(text)[next(t for t in sections(text) if t.split()[0] == version)]

    status_match = re.match(r"Status:\s*(.*?)(?:\n\s*\n|$)(.*)", body, re.DOTALL)
    if not status_match:
        raise SystemExit(f"{version}: changelog section must start with 'Status:'")
    status = " ".join(status_match.group(1).split())
    changes = status_match.group(2).strip()

    index = headings.index(version)
    previous = headings[index + 1] if index + 1 < len(headings) else "v0.1.0-beta"
    return status, changes, previous


def find_section(found, *names):
    for title, body in found.items():
        if any(name.lower() == title.lower() for name in names):
            return title, body
    return None, None


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--changelog", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    version = args.version
    out = args.out or args.zip.parent / "RELEASE_NOTES.md"
    status, changes, previous = changelog_entry(args.changelog.read_text(encoding="utf-8"), version)

    with zipfile.ZipFile(args.zip) as z:
        names = set(z.namelist())
        readme = sections(z.read("README.md").decode("utf-8"))
        known = sections(z.read("KNOWN_ISSUES.md").decode("utf-8"))
        source = z.read("SOURCE.md").decode("utf-8")
        dll_sha = hashlib.sha256(z.read("SKSE/Plugins/skydoomskse.dll")).hexdigest().upper()
    zip_sha = hashlib.sha256(args.zip.read_bytes()).hexdigest().upper()

    commit = re.search(r"Commit: `([0-9a-f]{40})`", source)
    if not commit:
        raise SystemExit("SOURCE.md in the zip has no commit")
    has_mcm = "SkyDoom.esp" in names

    how_title, how = find_section(readme, "How SkyDoom works now")
    controls_title, controls = find_section(readme, "Default controls", "Current controls")
    _, rough = find_section(known, "Current known rough edges")
    if controls is None or rough is None:
        raise SystemExit("README/KNOWN_ISSUES in the zip are missing expected sections")

    requirements = [
        "- **Skyrim Special Edition / Anniversary Edition**",
        "- **DOOM + DOOM II**",
        "- [SKSE 2.3.1 for Skyrim 1.7.104 (Steam)](https://www.nexusmods.com/skyrimspecialedition/mods/30379?tab=files)",
        "- [Address Library for SKSE Plugins](https://www.nexusmods.com/skyrimspecialedition/mods/32444)",
    ]
    if has_mcm:
        requirements += [
            "- [SkyUI](https://www.nexusmods.com/skyrimspecialedition/mods/12604)"
            " (for the in-game settings menu)",
            "- [MCM Helper](https://www.nexusmods.com/skyrimspecialedition/mods/53000)"
            " (for the in-game settings menu)",
        ]

    install = [
        "1. Install the correct SKSE version for your Skyrim runtime, and Address Library"
        + (". Install SkyUI and MCM Helper for the settings menu." if has_mcm else "."),
        f"2. Download **{args.zip.name}** from the Assets section below.",
        "3. If an earlier SkyDoom is installed, disable or remove it first.",
        "4. Install the ZIP with Vortex or Mod Organizer 2.",
    ]
    if has_mcm:
        install.append("5. Make sure `SkyDoom.esp` is enabled in your plugin list. It is a light"
                       " (ESL-flagged) plugin, so it does not use a full load order slot.")
    install += [
        f"{len(install) + 1}. Make sure your supported Steam copy of DOOM + DOOM II is installed.",
        f"{len(install) + 2}. Launch Skyrim through SKSE.",
    ]

    parts = [
        f"# SkyDoom {version} (test build)",
        "An unofficial test build of Caffs' **SkyDoom v0.1.0-beta** - DOOM running\n"
        "inside Skyrim through an SKSE/CommonLibSSE-NG bridge and a modified Chocolate\n"
        "Doom runtime - with changes from the SkyrimAIDev fork.",
        f"This is not an official SkyDoom release. For the official release, see\n{UPSTREAM_RELEASES}",
        wrap(f"**Status:** {status}", ""),
        f"## What's changed since {previous}\n\n{changes}",
    ]
    if how is not None:
        parts.append(f"## {how_title}\n\n{how}")
    parts += [
        "## Tested configuration\n\nSame target as v0.1.0-beta:\n\n"
        "- Skyrim runtime **1.7.104.0** (Steam)\n- **SKSE 2.3.1**\n"
        "- Steam **DOOM + DOOM II** installation using the current AppID 2280 layout\n"
        "- Windows 10/11\n\n"
        "Other Skyrim runtimes and non-Steam DOOM layouts have not yet been validated.",
        "## Requirements / game ownership\n\n"
        "SkyDoom does **not** include Skyrim or DOOM game files.\n\n"
        "To use the beta you need your own legitimate supported copies of:\n\n"
        + "\n".join(requirements)
        + "\n\nSteam DOOM + DOOM II:\n\nhttps://store.steampowered.com/app/2280/DOOM__DOOM_II/\n\n"
        "SkyDoom automatically discovers the player's own legitimate `DOOM.WAD` from\n"
        "their Steam libraries, so there is no need to manually copy DOOM WAD files\n"
        "into the mod.",
        "## Installation\n\n" + "\n".join(wrap(step, "   ") for step in install)
        + "\n\nDo not manually copy DOOM WAD files into the SkyDoom mod.",
        f"## {controls_title}\n\n{controls}",
        "## Included in this beta\n\n"
        "- Chocolate Doom weapon/HUD state bridged into Skyrim\n"
        "- Seven DOOM weapon slots\n"
        "- DOOM weapon damage against Skyrim NPCs\n"
        "- Rocket explosions with Skyrim-native knockback/ragdoll interaction\n"
        "- DOOM health, armour and ammunition state\n"
        "- Physical DOOM-style health/armour/ammo drops from Skyrim enemies\n"
        "- DOOM HUD and first-person weapon overlay\n"
        "- DOOM sound and standard Chocolate Doom music behaviour\n"
        "- Automatic Steam DOOM.WAD discovery\n"
        "- Portable bundled Chocolate Doom runtime",
        f"## Known rough edges\n\n{rough}",
        "## Source / licences\n\n"
        f"The full corresponding source for this build is at commit\n`{commit.group(1)}` on the "
        f"**release/{version}**\nbranch of {REPO_URL}\n\n"
        "- SkyDoom SKSE bridge: GPL-3.0\n- Modified Chocolate Doom: GPL-2.0\n"
        "- Third-party runtime notices are included in the binary package\n\n"
        "No proprietary DOOM or Skyrim game data is distributed with SkyDoom.",
        "## Credits\n\nSkyDoom was created by **Caffs**.\n\n"
        "SkyCraft by **chasmlol** was the inspiration for the original project. Huge\n"
        "credit to that project for demonstrating what was possible with\n"
        "passthrough-style integration.",
        f"## Checksums\n\n{args.zip.name} SHA256:\n\n`{zip_sha}`\n\n"
        f"The included skydoomskse.dll SHA256:\n\n`{dll_sha}`",
        "## Beta warning\n\nThis is an early beta test build. Expect bugs and compatibility limitations.\n\n"
        "When reporting a problem, please include your Skyrim runtime, SKSE version,\n"
        "DOOM installation details and the relevant SkyDoom/SKSE log if available.",
    ]

    text = "\n\n".join(parts) + "\n"
    bad = sorted({c for c in text if ord(c) > 127})
    if bad:
        raise SystemExit(f"non-ASCII characters in release notes: {bad}")
    out.write_text(text, encoding="ascii", newline="\n")
    print(f"{out} ({version}, status: {status[:60]}...)")


if __name__ == "__main__":
    main()
