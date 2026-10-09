"""Generate SkyDoom.esp, the light plugin that hosts SkyDoom's MCM.

The plugin holds a single quest, the layout MCM Helper expects (and that
mods such as Better Third Person Selection and TrueHUD ship):

  * QUST "SkyDoom_MCM": Start Game Enabled + Run Once, with the
    SkyDoom_MCM script (extends MCM_ConfigBase) attached;
  * one reference alias "PlayerAlias" forced to the player (0x14), with
    SkyUI's SKI_PlayerLoadGameAlias script so the menu re-registers on load.

The root .gitignore excludes *.esp, so the plugin is generated at package
time instead of being committed.

Usage: python -I make_mcm_esp.py <output SkyDoom.esp>
"""

import struct
import sys

QUEST_FORM_ID = 0x01000800  # first light-plugin object ID
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


def plugin():
    header = subrecord(b"HEDR", struct.pack("<fII", 1.70, 2, (QUEST_FORM_ID & 0xFFF) + 1))
    header += subrecord(b"CNAM", zstring("DEFAULT"))
    header += subrecord(b"MAST", zstring("Skyrim.esm"))
    header += subrecord(b"DATA", struct.pack("<Q", 0))
    header += subrecord(b"INTV", struct.pack("<I", 1))
    tes4 = record(b"TES4", 0, 0x200, header)  # 0x200 = ESL (light)
    return tes4 + group(b"QUST", quest())


if __name__ == "__main__":
    with open(sys.argv[1], "wb") as out:
        out.write(plugin())
