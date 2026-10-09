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

	struct Values
	{
		std::array<Binding, kActionCount> bindings{};

		// While SkyDoom is active, keep bound keys/buttons away from Skyrim.
		bool blockSkyrimInput = true;

		// Empty: discover DOOM.WAD in the user's Steam libraries.
		std::wstring wadPath;
	};

	[[nodiscard]] Values Defaults();

	// Loads the built-in defaults, then settings.ini, then the user file.
	[[nodiscard]] Values Load(const std::filesystem::path& a_dataDirectory);

	// INI key names, e.g. "iMeleeKey" / "iMeleeButton" (section [Controls]).
	[[nodiscard]] const char* KeyboardKeyName(Action a_action);
	[[nodiscard]] const char* GamepadKeyName(Action a_action);
}
