"use client";
export function FleetAiTranslatePanel({ services, active, translations, languages }: { services: number; active: number; translations: number; languages: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 AI Translation</h3>
    <div className="text-sm">{active}/{services} active · {translations.toLocaleString()} translations · {languages} languages</div>
  </div>);
}
