"""Generate SkyDoom.esp, the light plugin that hosts SkyDoom's MCM and the
DOOM minigame books.

The plugin holds a quest, the layout MCM Helper expects (and that mods such
as Better Third Person Selection and TrueHUD ship):

  * QUST "SkyDoom_MCM": Start Game Enabled + Run Once, with the
    SkyDoom_MCM script (extends MCM_ConfigBase) attached;
  * one reference alias "PlayerAlias" forced to the player (0x14), with
    SkyUI's SKI_PlayerLoadGameAlias script so the menu re-registers on load.

and two books, "Knee-Deep in the Dead" (SkyDoom_ArcadeBook, 0x801) and
"Hell on Earth" (SkyDoom_ArcadeBook2, 0x802). The SKSE plugin puts them in
boss chests (Bleak Falls Barrow, Ustengrav) and starts the DOOM or DOOM II
minigame when one is closed after reading (SKYDOOM_ARCADE, SKYDOOM_DOOM2).

The root .gitignore excludes *.esp, so the plugin is generated at package
time instead of being committed.

Usage: python -I make_mcm_esp.py <output SkyDoom.esp>
"""

import struct
import sys

QUEST_FORM_ID = 0x01000800  # first light-plugin object ID
BOOK_FORM_ID = 0x01000801  # kSkyDoomArcadeBookLocalIds in Plugin.cpp
BOOK2_FORM_ID = 0x01000802  # DOOM II
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

You will fight as you fight in DOOM, with whatever you can find. Your own weapons and armour stay behind, and what you find there stays there.

At the end of each level the gate asks whether you go on. Press Use to go deeper, or Esc (B on a controller) to return to where you stood. The book remembers where you stopped and what you carried.

Esc (Start on a controller) opens the gate's own menu: save, load, options, or quit back to Skyrim in the middle of a level.

If the way back is ever lost, hold the Toggle DOOM mode key.
</p>
"""


BOOK2_TEXT = """<p align="center">
<font size="36">HELL
ON EARTH</font>


A record of the
fall of Earth
</p>
[pagebreak]
<p align="left">
This book was not written. It was left behind.

Its pages smell of smoke and hot iron. Between the lines lies a city that is not Solitude or Markarth, its towers burning, its streets full of the same things that came through the gate before. This time they did not stop at the hangar.

Somewhere at the end of it is a wall with a face. It is waiting.
</p>
[pagebreak]
<p align="left">
Close this book to be pulled through.

As before, you fight with what you find, and what you find stays there. This gate keeps its own record of where you stopped, and its own saves.

At the end of each level the gate asks whether you go on. Press Use to go deeper, or Esc (B on a controller) to return to where you stood.

Esc (Start on a controller) opens the gate's own menu: save, load, options, or quit back to Skyrim in the middle of a level.

When the last of them falls, they pass before you one by one. Open the menu and quit when you have seen enough.

If the way back is ever lost, hold the Toggle DOOM mode key.
</p>
"""


def book(form_id, editor_id, name, model, text):
    data = subrecord(b"EDID", zstring(editor_id))
    data += subrecord(b"OBND", struct.pack("<6h", -9, -11, -1, 9, 11, 2))
    data += subrecord(b"FULL", zstring(name))
    data += subrecord(b"MODL", zstring(model))
    data += subrecord(b"DESC", zstring(text.replace("\n", "\r\n")))
    data += subrecord(b"KSIZ", struct.pack("<I", 1))
    data += subrecord(b"KWDA", struct.pack("<I", 0x000937A2))  # VendorItemBook
    # Flags, type (book), unused, teaches (none), value, weight. Worth
    # nothing and weightless: the plugin gives it back if it goes missing.
    data += subrecord(b"DATA", struct.pack("<BBHiIf", 0, 0, 0, -1, 0, 0.0))
    data += subrecord(b"INAM", struct.pack("<I", 0x00015417))  # vanilla book inventory art
    data += subrecord(b"CNAM", zstring(""))
    return record(b"BOOK", form_id, 0, data)


def plugin():
    # HEDR: version, number of records and groups, next object ID.
    header = subrecord(b"HEDR", struct.pack("<fII", 1.70, 5, (BOOK2_FORM_ID & 0xFFF) + 1))
    header += subrecord(b"CNAM", zstring("DEFAULT"))
    header += subrecord(b"MAST", zstring("Skyrim.esm"))
    header += subrecord(b"DATA", struct.pack("<Q", 0))
    header += subrecord(b"INTV", struct.pack("<I", 1))
    tes4 = record(b"TES4", 0, 0x200, header)  # 0x200 = ESL (light)
    # Top-level groups in the game's order: BOOK comes before QUST.
    books = book(BOOK_FORM_ID, "SkyDoom_ArcadeBook", "Knee-Deep in the Dead",
                 "Clutter\\Books\\BasicBook07.nif", BOOK_TEXT)
    books += book(BOOK2_FORM_ID, "SkyDoom_ArcadeBook2", "Hell on Earth",
                  "Clutter\\Books\\BasicBook03.nif", BOOK2_TEXT)
    return tes4 + group(b"BOOK", books) + group(b"QUST", quest())


if __name__ == "__main__":
    with open(sys.argv[1], "wb") as out:
        out.write(plugin())
