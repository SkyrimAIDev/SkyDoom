"""Build SkyDoom's MCM data files into a Skyrim Data-folder layout.

Produces, under <out>:
  SkyDoom.esp                              (tools/make_mcm_esp.py)
  Scripts/SkyDoom_MCM.pex                  (compiled with the CK compiler)
  Source/Scripts/SkyDoom_MCM.psc
  MCM/Config/SkyDoom/config.json, settings.ini

Requirements:
  * Creation Kit's PapyrusCompiler.exe and the vanilla script sources
    (Data/Source/Scripts, containing TESV_Papyrus_Flags.flg);
  * MCM Helper's public script sources (MCM_ConfigBase.psc,
    SKI_ConfigBase.psc, SKI_QuestBase.psc): the scripts/public folder of
    https://github.com/Exit-9B/MCM-Helper at tag v1.6.2.

Usage:
  python -I build_mcm.py --out <dir> --compiler <PapyrusCompiler.exe>
      --skyrim-scripts <Data/Source/Scripts> --mcm-helper-scripts <scripts/public>
"""

import argparse
import importlib.util
import shutil
import struct
import subprocess
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
DATA = TOOLS.parent / "data"

# Load the sibling generator by path, so this also works under `python -I`.
_spec = importlib.util.spec_from_file_location("make_mcm_esp", TOOLS / "make_mcm_esp.py")
make_mcm_esp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_mcm_esp)


def scrub_pex_header(path):
    """Replace the builder's user and machine names that PapyrusCompiler
    stamps into the .pex header (informational only; never read by the game).

    Header (big-endian): magic u32, major u8, minor u8, game u16, compile
    time u64, then source / user / machine names as u16-length strings.
    """
    data = path.read_bytes()
    if data[:4] != b"\xFA\x57\xC0\xDE":
        raise SystemExit(f"{path} is not a Skyrim .pex file")

    offset = 16
    fields = []
    for _ in range(3):
        (length,) = struct.unpack_from(">H", data, offset)
        fields.append(data[offset + 2:offset + 2 + length])
        offset += 2 + length

    def wstring(value):
        return struct.pack(">H", len(value)) + value

    header = data[:16] + wstring(fields[0]) + wstring(b"SkyDoom") + wstring(b"SkyDoom")
    path.write_bytes(header + data[offset:])


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--compiler", required=True, type=Path)
    parser.add_argument("--skyrim-scripts", required=True, type=Path)
    parser.add_argument("--mcm-helper-scripts", required=True, type=Path)
    args = parser.parse_args()

    out = args.out
    (out / "Scripts").mkdir(parents=True, exist_ok=True)

    (out / "SkyDoom.esp").write_bytes(make_mcm_esp.plugin())

    for rel in ("MCM/Config/SkyDoom/config.json", "MCM/Config/SkyDoom/settings.ini",
                "Source/Scripts/SkyDoom_MCM.psc"):
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DATA / rel, out / rel)

    source_dir = DATA / "Source" / "Scripts"
    imports = ";".join(str(p) for p in (source_dir, args.mcm_helper_scripts, args.skyrim_scripts))
    subprocess.run(
        [
            str(args.compiler),
            "SkyDoom_MCM.psc",
            "-f=" + str(args.skyrim_scripts / "TESV_Papyrus_Flags.flg"),
            "-i=" + imports,
            "-o=" + str(out / "Scripts"),
            "-op",
        ],
        cwd=source_dir,
        check=True,
    )

    pex = out / "Scripts" / "SkyDoom_MCM.pex"
    if not pex.is_file():
        raise SystemExit("PapyrusCompiler did not produce SkyDoom_MCM.pex")

    scrub_pex_header(pex)

    print(f"MCM data written to {out}")


if __name__ == "__main__":
    main()
