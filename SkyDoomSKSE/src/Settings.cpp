#include "Settings.h"

#include <charconv>
#include <cmath>
#include <fstream>
#include <iterator>
#include <map>
#include <string_view>

namespace SkyDoom::Settings
{
	namespace
	{
		struct ActionInfo
		{
			const char* keyboardKey;
			const char* gamepadKey;
			std::int32_t keyboardDefault;
			std::int32_t gamepadDefault;
		};

		// Keyboard defaults keep v0.1.0-beta's layout (LMB, 1-7, F10).
		// Controller defaults: Right Trigger fires, D-pad Right/Left cycle
		// weapons.
		constexpr std::array<ActionInfo, kActionCount> kActions{ {
			{ "iFireKey", "iFireButton", 256, 281 },                         // LMB, RT
			{ "iMeleeKey", "iMeleeButton", 0x02, kUnbound },                 // 1
			{ "iPistolKey", "iPistolButton", 0x03, kUnbound },               // 2
			{ "iShotgunKey", "iShotgunButton", 0x04, kUnbound },             // 3
			{ "iChaingunKey", "iChaingunButton", 0x05, kUnbound },           // 4
			{ "iRocketKey", "iRocketButton", 0x06, kUnbound },               // 5
			{ "iPlasmaKey", "iPlasmaButton", 0x07, kUnbound },               // 6
			{ "iBfgKey", "iBfgButton", 0x08, kUnbound },                     // 7
			{ "iNextWeaponKey", "iNextWeaponButton", kUnbound, 269 },        // D-pad Right
			{ "iPrevWeaponKey", "iPrevWeaponButton", kUnbound, 268 },        // D-pad Left
			{ "iMusicToggleKey", "iMusicToggleButton", 0x44, kUnbound },     // F10
			{ "iToggleDoomKey", "iToggleDoomButton", 0x57, kUnbound },       // F11
		} };

		// Highest SKSE key code (gamepad right trigger).
		constexpr std::int32_t kMaxKeyCode = 281;

		using Section = std::map<std::string, std::string>;
		using IniFile = std::map<std::string, Section>;

		std::string ToLower(std::string_view a_text)
		{
			std::string result(a_text);
			for (auto& ch : result) {
				if (ch >= 'A' && ch <= 'Z') {
					ch = static_cast<char>(ch - 'A' + 'a');
				}
			}
			return result;
		}

		std::string_view Trim(std::string_view a_text)
		{
			const auto first = a_text.find_first_not_of(" \t\r\n");
			if (first == std::string_view::npos) {
				return {};
			}
			return a_text.substr(first, a_text.find_last_not_of(" \t\r\n") - first + 1);
		}

		// Minimal UTF-8 INI reader. Section and key names are case-insensitive;
		// lines starting with ';' or '#' are comments.
		bool ReadIni(const std::filesystem::path& a_path, IniFile& a_ini)
		{
			std::ifstream file(a_path, std::ios::binary);
			if (!file) {
				return false;
			}

			const std::string text(
				(std::istreambuf_iterator<char>(file)),
				std::istreambuf_iterator<char>());

			std::string_view rest(text);
			if (rest.starts_with("\xEF\xBB\xBF")) {
				rest.remove_prefix(3);
			}

			std::string section;
			while (!rest.empty()) {
				const auto newline = rest.find('\n');
				const auto line = Trim(rest.substr(0, newline));
				rest = newline == std::string_view::npos ? std::string_view{} : rest.substr(newline + 1);

				if (line.empty() || line.front() == ';' || line.front() == '#') {
					continue;
				}

				if (line.front() == '[' && line.back() == ']') {
					section = ToLower(Trim(line.substr(1, line.size() - 2)));
					continue;
				}

				const auto equals = line.find('=');
				if (equals == std::string_view::npos) {
					continue;
				}

				a_ini[section][ToLower(Trim(line.substr(0, equals)))] =
					std::string(Trim(line.substr(equals + 1)));
			}

			return true;
		}

		const std::string* Find(const IniFile& a_ini, std::string_view a_section, std::string_view a_key)
		{
			const auto section = a_ini.find(ToLower(a_section));
			if (section == a_ini.end()) {
				return nullptr;
			}
			const auto value = section->second.find(ToLower(a_key));
			return value == section->second.end() ? nullptr : &value->second;
		}

		void ReadKeyCode(const IniFile& a_ini, const char* a_key, std::int32_t& a_value)
		{
			const auto* text = Find(a_ini, "Controls", a_key);
			if (!text) {
				return;
			}

			std::int32_t parsed = 0;
			const auto* end = text->data() + text->size();
			const auto [ptr, ec] = std::from_chars(text->data(), end, parsed);

			// -1 means unbound; 0 is not a valid key code.
			if (ec == std::errc{} && ptr == end && (parsed == kUnbound || (parsed > 0 && parsed <= kMaxKeyCode))) {
				a_value = parsed;
			}
		}

		void ReadBool(const IniFile& a_ini, std::string_view a_section, std::string_view a_key, bool& a_value)
		{
			const auto* text = Find(a_ini, a_section, a_key);
			if (!text) {
				return;
			}

			const auto lower = ToLower(*text);
			if (lower == "1" || lower == "true") {
				a_value = true;
			} else if (lower == "0" || lower == "false") {
				a_value = false;
			}
		}

		// Integer setting accepted only within [a_min, a_max].
		void ReadInt(
			const IniFile& a_ini, std::string_view a_section, std::string_view a_key,
			std::int32_t a_min, std::int32_t a_max, std::int32_t& a_value)
		{
			const auto* text = Find(a_ini, a_section, a_key);
			if (!text) {
				return;
			}

			std::int32_t parsed = 0;
			const auto* end = text->data() + text->size();
			const auto [ptr, ec] = std::from_chars(text->data(), end, parsed);

			if (ec == std::errc{} && ptr == end && parsed >= a_min && parsed <= a_max) {
				a_value = parsed;
			}
		}

		// Finite float setting accepted only within [a_min, a_max].
		void ReadFloat(
			const IniFile& a_ini, std::string_view a_section, std::string_view a_key,
			float a_min, float a_max, float& a_value)
		{
			const auto* text = Find(a_ini, a_section, a_key);
			if (!text) {
				return;
			}

			float parsed = 0.0f;
			const auto* end = text->data() + text->size();
			const auto [ptr, ec] = std::from_chars(text->data(), end, parsed);

			if (ec == std::errc{} && ptr == end && std::isfinite(parsed) && parsed >= a_min && parsed <= a_max) {
				a_value = parsed;
			}
		}

		void ReadPath(const IniFile& a_ini, std::string_view a_section, std::string_view a_key, std::wstring& a_value)
		{
			const auto* text = Find(a_ini, a_section, a_key);
			if (!text) {
				return;
			}

			if (text->empty()) {
				a_value.clear();
				return;
			}

			const auto length = MultiByteToWideChar(
				CP_UTF8, MB_ERR_INVALID_CHARS, text->data(), static_cast<int>(text->size()), nullptr, 0);
			if (length <= 0) {
				return;
			}

			std::wstring wide(static_cast<std::size_t>(length), L'\0');
			MultiByteToWideChar(
				CP_UTF8, MB_ERR_INVALID_CHARS, text->data(), static_cast<int>(text->size()), wide.data(), length);
			a_value = std::move(wide);
		}

		void Apply(const IniFile& a_ini, Values& a_values)
		{
			for (std::size_t i = 0; i < kActionCount; ++i) {
				ReadKeyCode(a_ini, kActions[i].keyboardKey, a_values.bindings[i].keyboard);
				ReadKeyCode(a_ini, kActions[i].gamepadKey, a_values.bindings[i].gamepad);
			}

			ReadBool(a_ini, "Controls", "bBlockSkyrimInput", a_values.blockSkyrimInput);
			ReadPath(a_ini, "General", "sWadPath", a_values.wadPath);

			ReadBool(a_ini, "General", "bEnabled", a_values.enabled);
			ReadBool(a_ini, "General", "bKeepStaminaFull", a_values.keepStaminaFull);

			auto combatMode = static_cast<std::int32_t>(a_values.combatMode);
			ReadInt(a_ini, "General", "iCombatMode", 0, 1, combatMode);
			a_values.combatMode = static_cast<CombatMode>(combatMode);

			auto musicMode = static_cast<std::int32_t>(a_values.musicMode);
			ReadInt(a_ini, "General", "iMusicMode", 0, 2, musicMode);
			a_values.musicMode = static_cast<MusicMode>(musicMode);

			ReadFloat(a_ini, "Balance", "fDamageDealtMult", 0.1f, 10.0f, a_values.damageDealtMult);
			ReadFloat(a_ini, "Balance", "fDamageTakenMult", 0.1f, 5.0f, a_values.damageTakenMult);
		}
	}

	Values Defaults()
	{
		Values values;
		for (std::size_t i = 0; i < kActionCount; ++i) {
			values.bindings[i].keyboard = kActions[i].keyboardDefault;
			values.bindings[i].gamepad = kActions[i].gamepadDefault;
		}
		return values;
	}

	Values Load(const std::filesystem::path& a_dataDirectory)
	{
		auto values = Defaults();

		for (const auto& file : {
				 a_dataDirectory / "MCM" / "Config" / "SkyDoom" / "settings.ini",
				 a_dataDirectory / "MCM" / "Settings" / "SkyDoom.ini" }) {
			IniFile ini;
			if (ReadIni(file, ini)) {
				Apply(ini, values);
			}
		}

		return values;
	}

	const char* KeyboardKeyName(Action a_action)
	{
		return kActions[static_cast<std::size_t>(a_action)].keyboardKey;
	}

	const char* GamepadKeyName(Action a_action)
	{
		return kActions[static_cast<std::size_t>(a_action)].gamepadKey;
	}
}
