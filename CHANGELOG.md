# SkyDoom fork changelog

Test builds from the SkyrimAIDev fork of Caffs' SkyDoom v0.1.0-beta, newest
first. Each build is made from its `release/<version>` branch, and its
`RELEASE_NOTES.md` is generated from the matching section below by
`SkyDoomSKSE/tools/make_release_notes.py`.

Each section starts with a `Status:` line (how far the build has been
tested), followed by the changes since the previous build.

## v0.1.6-beta - 2026-10-09

Status: In testing.

- New: DOOM stashes in dungeons. The first time you enter a dungeon area in
  a session, a few DOOM items appear on top of its chests, barrels and urns,
  chosen by what you are lowest on.
- New: MCM General page: Enable SkyDoom, DOOM combat (when a weapon is drawn
  or always), DOOM music (in DOOM combat, always or off), and Keep stamina
  full in DOOM combat.
- New: MCM Balance page: DOOM weapon damage multiplier (0.1x-10x) and
  damage taken in DOOM combat multiplier (0.1x-5x).
- New: MCM Pickups page: turn enemy drops on or off, set the drop chance,
  and turn dungeon stashes on or off.
- Fixed: a DOOM item left in one interior could appear, and be picked up,
  at the same spot in a different interior.

## v0.1.5-beta - 2026-10-09

Status: In testing. So far drawing and sheathing switch between DOOM combat
and Skyrim as intended.

- New: DOOM combat mode. With DOOM mode on, drawing a weapon switches to
  DOOM combat: DOOM HUD and weapons, DOOM controls, DOOM health and DOOM
  music, with Skyrim's attack and block switched off. Sheathe to return to
  normal Skyrim. Previously SkyDoom took over Skyrim combat all the time and
  you could not draw a Skyrim weapon.
- New: Toggle DOOM mode (F11 by default; set a controller button in the MCM)
  replaces v0.1.4-beta's Toggle DOOM HUD. With DOOM mode off, Skyrim plays
  normally.
- Changed: DOOM health and DOOM music only apply in DOOM combat. Outside it,
  Skyrim health and music work normally.
- Changed: stamina stays full in DOOM combat, since the DOOM HUD has no
  stamina meter.
- Changed: with DOOM mode off, enemies do not drop DOOM pickups.

## v0.1.4-beta - 2026-10-09

Status: Built but not tested; superseded by v0.1.5-beta.

- Fixed: the DOOM HUD and weapon covered Skyrim's dialogue (and other menus
  that do not pause the game). SkyDoom now hides everything it draws while a
  menu or dialogue is open.
- New: Toggle DOOM HUD (F11 by default) shows or hides the DOOM HUD and
  weapon.

## v0.1.3-beta - 2026-10-09

Status: Tested on Skyrim 1.6.1170 with SKSE 2.2.6 (NGVO). Dying from your
own rocket no longer crashes. A rocket box picked up after a death was
correctly refused (standard DOOM: the backpack is lost on death, so rockets
were already full). Right Trigger fire not yet confirmed.

- Fixed: Skyrim could crash while reloading after the player died. SkyDoom
  now only updates Skyrim's crosshair from the game's UI thread.
- Fixed: the Right Trigger did not fire DOOM weapons on some controller
  setups. Fire is now its own binding (left mouse button / Right Trigger by
  default) and can be changed in the MCM.

## v0.1.2-beta - 2026-10-09

Status: Tested on Skyrim 1.6.1170 with SKSE 2.2.6 (NGVO). The MCM appeared
and D-pad Left/Right switched DOOM weapons. Found two problems, both fixed in
v0.1.3-beta: the Right Trigger did not fire, and Skyrim crashed while
reloading after a death.

- New: controller support. Next / previous weapon is on D-pad Right / Left by
  default, and every DOOM action can have both a keyboard/mouse binding and a
  controller binding.
- New: a SkyDoom page in the Mod Configuration Menu (needs SkyUI and MCM
  Helper) to rebind controls, choose whether SkyDoom's buttons are kept from
  Skyrim, and set a DOOM.WAD location for non-Steam installs.
- Changed: while SkyDoom is active, keys and buttons bound to SkyDoom no
  longer also trigger their Skyrim action. For example, 1-7 no longer equip
  favourites. This can be turned off in the MCM.
- Hardening: Skyrim and DOOM now talk through a private, per-session channel
  that other programs cannot find by name, and a testing-only option that
  could launch a different program has been removed from release builds.

## v0.1.1-beta - 2026-10-09

Status: Tested on Skyrim 1.6.1170 with SKSE 2.2.6 (NGVO) for about 30
minutes with no issues: all weapons, pickups including healing, and death
followed by a reload.

- Fixed: the DOOM guest could hang if its shared input queue was corrupted.
  It now processes at most one queue's worth of input per tic.
- Fixed: very large incoming damage values could overflow and be lost.
- Fixed: Skyrim could crash if the overlay hook was only partly installed.
- Fixed: pistol damage reported by DOOM is now checked against what the DOOM
  pistol can actually deal (at most 15 per shot).
- Fixed: running the bundled `chocolate-doom.exe` on its own no longer
  attaches to a running Skyrim session, no longer crashes on the title
  screen, and fires rockets, plasma and BFG shots normally.
- The published source now builds from a clean checkout. Build files that
  were missing from the v0.1.0-beta source have been restored.
