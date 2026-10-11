Scriptname SkyDoom_MCM extends MCM_ConfigBase
{SkyDoom's MCM page, built by MCM Helper from MCM\Config\SkyDoom\config.json.
OnConfigClose, GiveBook and GiveDoom2Book are implemented by the SkyDoom SKSE
plugin: OnConfigClose reloads its settings whenever the menu closes, and
GiveBook and GiveDoom2Book (the Minigame page's buttons) give the player the
DOOM and DOOM II minigame books.}

Function OnConfigClose() Native

Function GiveBook() Native

Function GiveDoom2Book() Native
