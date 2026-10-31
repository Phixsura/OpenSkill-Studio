"use client";

interface LocaleInfo { locale: string; label: string; completeness: number; }

const flags: Record<string, string> = { en: "🇺🇸", zh: "🇨🇳", ja: "🇯🇵", ko: "🇰🇷", fr: "🇫🇷", de: "🇩🇪", es: "🇪🇸", pt: "🇧🇷", ru: "🇷🇺", ar: "🇸🇦" };

export function LocaleSwitcher({ locales, selected, onSelect }: {
  locales: LocaleInfo[]; selected: string; onSelect?: (locale: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-1">
      {locales.map(l => (
        <button key={l.locale} onClick={() => onSelect?.(l.locale)}
          className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full border ${
            selected === l.locale ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "border-gray-200 dark:border-gray-700"
          }`}>
          <span>{flags[l.locale] || "🌐"}</span>
          <span>{l.label}</span>
          {l.completeness < 100 && (
            <span className={`text-[10px] px-1 rounded ${l.completeness === 0 ? "bg-red-100 text-red-600" : "bg-yellow-100 text-yellow-600"}`}>
              {l.completeness}%
            </span>
          )}
        </button>
      ))}
    </div>
  );
}
