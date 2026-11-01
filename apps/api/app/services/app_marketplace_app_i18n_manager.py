"""i18n manager — internationalization key management."""


def get_translation_coverage(*, translations: dict[str, dict[str, str]],
                                base_locale: str = "en") -> dict:
    base_keys = set(translations.get(base_locale, {}).keys())
    if not base_keys:
        return {"error": "Base locale has no keys"}
    coverage = []
    for locale, strings in translations.items():
        translated = set(strings.keys()) & base_keys
        missing = base_keys - set(strings.keys())
        pct = round(len(translated) / len(base_keys) * 100, 1)
        coverage.append({
            "locale": locale,
            "translated": len(translated),
            "missing": len(missing),
            "missing_keys": sorted(missing)[:10],
            "coverage_pct": pct,
            "complete": pct == 100,
        })
    coverage.sort(key=lambda c: c["coverage_pct"], reverse=True)
    return {"base_locale": base_locale, "total_keys": len(base_keys),
            "locales": coverage, "fully_translated": sum(1 for c in coverage if c["complete"])}


def find_unused_keys(*, used_keys: set[str], defined_keys: set[str]) -> dict:
    unused = sorted(defined_keys - used_keys)
    missing = sorted(used_keys - defined_keys)
    return {"unused": unused, "missing_in_code": missing,
            "unused_count": len(unused), "missing_count": len(missing)}
