"""Generate SkyDoom.esp, the light plugin that hosts SkyDoom's MCM and the
DOOM minigame book.

The plugin holds a quest, the layout MCM Helper expects (and that mods such
as Better Third Person Selection and TrueHUD ship):

  * QUST "SkyDoom_MCM": Start Game Enabled + Run Once, with the
    SkyDoom_MCM script (extends MCM_ConfigBase) attached;
  * one reference alias "PlayerAlias" forced to the player (0x14), with
    SkyUI's SKI_PlayerLoadGameAlias script so the menu re-registers on load.

and a book, "Knee-Deep in the Dead" (SkyDoom_ArcadeBook, 0x801). The SKSE
plugin puts it in the player's inventory and starts the DOOM minigame when
it is closed after reading (SKYDOOM_ARCADE).

The root .gitignore excludes *.esp, so the plugin is generated at package
time instead of being committed.

Usage: python -I make_mcm_esp.py <output SkyDoom.esp>
"""

import struct
import sys

QUEST_FORM_ID = 0x01000800  # first light-plugin object ID
BOOK_FORM_ID = 0x01000801  # kSkyDoomArcadeBookLocalId in Plugin.cpp
FORM_VERSION = 44  # Skyrim SE


def zstring(text):
    return text.encode("ascii") + b"\0"


def wstring(text):
    data = text.encode("ascii")
    return struct.pack("<H", len(data)) + data


def subrecord(tag, data):
    return tag + struct.pack("<H", len(data)) + data


def record(tag, form_id, flags, data):
    # type, data size, flags, FormID, version control, form version, unknown
    return tag + struct.pack("<IIIIHH", len(data), flags, form_id, 0, FORM_VERSION, 0) + data


def group(label, data):
    # type, group size (incl. header), label, group type, stamp, vc, unknown
    return b"GRUP" + struct.pack("<I", 24 + len(data)) + label + struct.pack("<iHHI", 0, 0, 0, 0) + data


def script(name):
    # name, status, property count
    return wstring(name) + struct.pack("<BH", 0, 0)


def vmad():
    data = struct.pack("<hhH", 5, 2, 1) + script("SkyDoom_MCM")
    # Quest fragments: unknown, fragment count, file name.
    data += struct.pack("<bH", 2, 0) + wstring("")
    # One alias script block. Object format 2: unused, alias ID, FormID.
    data += struct.pack("<H", 1)
    data += struct.pack("<HhI", 0, 0, QUEST_FORM_ID)
    data += struct.pack("<hhH", 5, 2, 1) + script("SKI_PlayerLoadGameAlias")
    return data


def quest():
    data = subrecord(b"EDID", zstring("SkyDoom_MCM"))
    data += subrecord(b"VMAD", vmad())
    data += subrecord(b"FULL", zstring("SkyDoom MCM"))
    # Flags (Start Game Enabled | Run Once), priority, form version byte,
    # unknown, type.
    data += subrecord(b"DNAM", struct.pack("<HBBII", 0x0101, 0, 0xB0, 0, 0))
    data += subrecord(b"NEXT", b"")
    data += subrecord(b"ANAM", struct.pack("<I", 1))  # next alias ID
    data += subrecord(b"ALST", struct.pack("<I", 0))
    data += subrecord(b"ALID", zstring("PlayerAlias"))
    data += subrecord(b"FNAM", struct.pack("<I", 0))
    data += subrecord(b"ALFR", struct.pack("<I", 0x14))  # PlayerRef
    data += subrecord(b"VTCK", struct.pack("<I", 0))
    data += subrecord(b"ALED", b"")
    return record(b"QUST", QUEST_FORM_ID, 0, data)


BOOK_TEXT = """<p align="center">
<font size="36">KNEE-DEEP
IN THE DEAD</font>


A record of the
Phobos Anomaly
</p>
[pagebreak]
<p align="left">
The binding is warm, as if something on the other side of the pages is breathing. The words do not stay still. They crawl into corridors of metal and stone, lit by a red that no forge in Skyrim has ever made.

Somewhere beyond them is a gate, and beyond the gate is a hangar full of the dead who did not stay dead.

You have the feeling the book wants to be finished. Not read. Finished.
</p>
[pagebreak]
<p align="left">
Close this book to be pulled through.

You will fight as you fight in DOOM, with whatever you can find. Your own weapons and armour stay behind.

Reach the exit of the level and the gate lets you go, back to where you stood.

If the way back is ever lost, hold the Toggle DOOM mode key.
</p>
"""


def book():
    data = subrecord(b"EDID", zstring("SkyDoom_ArcadeBook"))
    data += subrecord(b"OBND", struct.pack("<6h", -9, -11, -1, 9, 11, 2))
    data += subrecord(b"FULL", zstring("Knee-Deep in the Dead"))
    data += subrecord(b"MODL", zstring("Clutter\\Books\\BasicBook07.nif"))
    data += subrecord(b"DESC", zstring(BOOK_TEXT.replace("\n", "\r\n")))
    data += subrecord(b"KSIZ", struct.pack("<I", 1))
    data += subrecord(b"KWDA", struct.pack("<I", 0x000937A2))  # VendorItemBook
    # Flags, type (book), unused, teaches (none), value, weight. Worth
    # nothing and weightless: the plugin gives it back if it goes missing.
    data += subrecord(b"DATA", struct.pack("<BBHiIf", 0, 0, 0, -1, 0, 0.0))
    data += subrecord(b"INAM", struct.pack("<I", 0x00015417))  # vanilla book inventory art
    data += subrecord(b"CNAM", zstring(""))
    return record(b"BOOK", BOOK_FORM_ID, 0, data)


def plugin():
    # HEDR: version, number of records and groups, next object ID.
    header = subrecord(b"HEDR", struct.pack("<fII", 1.70, 4, (BOOK_FORM_ID & 0xFFF) + 1))
    header += subrecord(b"CNAM", zstring("DEFAULT"))
    header += subrecord(b"MAST", zstring("Skyrim.esm"))
    header += subrecord(b"DATA", struct.pack("<Q", 0))
    header += subrecord(b"INTV", struct.pack("<I", 1))
    tes4 = record(b"TES4", 0, 0x200, header)  # 0x200 = ESL (light)
    # Top-level groups in the game's order: BOOK comes before QUST.
    return tes4 + group(b"BOOK", book()) + group(b"QUST", quest())


if __name__ == "__main__":
    with open(sys.argv[1], "wb") as out:
        out.write(plugin())
