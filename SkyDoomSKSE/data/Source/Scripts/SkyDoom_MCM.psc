Scriptname SkyDoom_MCM extends MCM_ConfigBase
{SkyDoom's MCM page, built by MCM Helper from MCM\Config\SkyDoom\config.json.
OnConfigClose and GiveBook are implemented by the SkyDoom SKSE plugin:
OnConfigClose reloads its settings whenever the menu closes, and GiveBook
(the Minigame page's button) gives the player the DOOM minigame book.}

Function OnConfigClose() Native

Function GiveBook() Native
