"use client";

interface LocaleCoverage { locale: string; translated: number; missing: number;
  coverage_pct: number; complete: boolean; }
interface I18nCoverageGridProps { locales: LocaleCoverage[]; totalKeys: number;
  fullyTranslated: number; }

export function I18nCoverageGrid({ locales, totalKeys, fullyTranslated }: I18nCoverageGridProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Translations</h2>
        <span className="text-xs text-gray-400">{fullyTranslated}/{locales.length} complete · {totalKeys} keys</span>
      </div>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {locales.map(l => (
          <div key={l.locale} className={`rounded-lg border p-3 ${l.complete ? "border-green-200 dark:border-green-800" : "dark:border-gray-700"}`}>
            <div className="flex items-center justify-between">
              <span className="font-mono text-sm font-bold">{l.locale}</span>
              <span className={`text-xs ${l.complete ? "text-green-600" : "text-yellow-600"}`}>
                {l.coverage_pct}%
              </span>
            </div>
            <div className="mt-1.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${l.complete ? "bg-green-500" : "bg-yellow-500"}`}
                style={{ width: `${l.coverage_pct}%` }} />
            </div>
            <p className="mt-1 text-xs text-gray-400">{l.translated}/{totalKeys} · {l.missing} missing</p>
          </div>
        ))}
      </div>
    </div>
  );
}
