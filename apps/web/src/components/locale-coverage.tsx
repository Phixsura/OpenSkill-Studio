"use client";

interface LocaleInfo { locale: string; coveragePct: number; complete: boolean; missingCount: number; }
interface LocaleCoverageProps { locales: LocaleInfo[]; baseKeys: number; }

export function LocaleCoverage({ locales, baseKeys }: LocaleCoverageProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Translation Coverage</h3>
        <span className="text-xs text-gray-400">{baseKeys} base keys</span>
      </div>
      <div className="space-y-2">
        {locales.map(l => (
          <div key={l.locale} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="font-medium uppercase">{l.locale}</span>
                {l.complete && <span className="text-xs text-green-600">✓ Complete</span>}
              </div>
              <span className="text-xs text-gray-400">{l.coveragePct}%{l.missingCount > 0 ? ` · ${l.missingCount} missing` : ""}</span>
            </div>
            <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full transition-all ${l.complete ? "bg-green-500" : "bg-yellow-500"}`}
                style={{ width: `${l.coveragePct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
