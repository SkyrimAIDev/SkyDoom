#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <string>

/**
 * SkyDoom user settings, stored in MCM Helper's layout:
 *
 *   Data\MCM\Config\SkyDoom\settings.ini   defaults shipped with the mod
 *   Data\MCM\Settings\SkyDoom.ini          the user's changes (MCM Helper)
 *
 * Both are optional; built-in defaults apply when a key is missing.
 */
namespace SkyDoom::Settings
{
	// DOOM-side actions that can be bound. Fire is held (press and release
	// are both sent); the others act on press.
	enum class Action : std::size_t
	{
		Fire,
		Melee,
		Pistol,
		Shotgun,
		Chaingun,
		Rocket,
		Plasma,
		Bfg,
		NextWeapon,
		PrevWeapon,
		MusicToggle,
		ToggleDoom,

		kTotal
	};

	inline constexpr std::size_t kActionCount =
		static_cast<std::size_t>(Action::kTotal);

	inline constexpr std::int32_t kUnbound = -1;

	// SKSE/SkyUI key codes: keyboard DIK 0-255, mouse 256-265,
	// gamepad 266-281.
	struct Binding
	{
		std::int32_t keyboard = kUnbound;
		std::int32_t gamepad = kUnbound;
	};

	// When DOOM combat mode applies (MCM enum index).
	enum class CombatMode : std::int32_t
	{
		WeaponDrawn = 0,  // only while a weapon is drawn
		Always = 1,       // whenever SkyDoom is enabled
	};

	// When DOOM music may play (MCM enum index).
	enum class MusicMode : std::int32_t
	{
		Combat = 0,  // in DOOM combat mode
		Always = 1,  // whenever SkyDoom is enabled
		Off = 2,
	};

	struct Values
	{
		std::array<Binding, kActionCount> bindings{};

		// While SkyDoom is active, keep bound keys/buttons away from Skyrim.
		bool blockSkyrimInput = true;

		// Empty: discover DOOM.WAD in the user's Steam libraries.
		std::wstring wadPath;

		// [General]
		bool enabled = true;
		CombatMode combatMode = CombatMode::WeaponDrawn;
		MusicMode musicMode = MusicMode::Combat;
		bool keepStaminaFull = true;

		// Switch from third to first person when DOOM combat starts.
		bool firstPersonInCombat = true;

		// Point-blank DOOM shotgun blasts break door and container locks.
		bool shotgunBreaksLocks = true;

		// DOOM rocket blasts open any door, even ones that need a key.
		// Off by default: it can skip puzzles and break quests.
		bool rocketBustsDoors = false;

		// [Balance] multipliers: DOOM weapon damage against Skyrim actors,
		// and Skyrim damage before it reaches DOOM health.
		float damageDealtMult = 1.0f;  // 0.1 - 10
		float damageTakenMult = 1.0f;  // 0.1 - 5

		// [Pickups] DOOM items dropped by killed enemies.
		bool enemyDrops = true;
		std::int32_t enemyDropChance = 100;  // percent

		// DOOM items placed in dungeons the first time they are entered.
		bool worldStashes = true;
	};

	[[nodiscard]] Values Defaults();

	// Loads the built-in defaults, then settings.ini, then the user file.
	[[nodiscard]] Values Load(const std::filesystem::path& a_dataDirectory);

	// INI key names, e.g. "iMeleeKey" / "iMeleeButton" (section [Controls]).
	[[nodiscard]] const char* KeyboardKeyName(Action a_action);
	[[nodiscard]] const char* GamepadKeyName(Action a_action);
}
