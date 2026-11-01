"use client";
export function FleetI18nPanel({ totalStrings, translated, coveragePct, languages, ready }: { totalStrings: number; translated: number; coveragePct: number; languages: number; ready: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 i18n Coverage</h3>
    <div className="text-sm">{coveragePct}% translated · {languages} languages</div>
    {!ready && <span className="text-xs text-yellow-600">⚠️ Not localization-ready</span>}
  </div>);
}
