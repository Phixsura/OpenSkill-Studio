"use client";

interface LocaleProgress { locale: string; completeness_pct: number; missing_count: number; }
interface TranslationProgressCardProps { locales: LocaleProgress[]; baseLocale: string; }

export function TranslationProgressCard({ locales, baseLocale }: TranslationProgressCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Translation Progress</h3>
      <p className="mt-1 text-xs text-gray-400">Base: {baseLocale}</p>
      <ul className="mt-3 space-y-2">
        {locales.map(l => (
          <li key={l.locale}>
            <div className="flex justify-between text-sm">
              <span className="font-medium">{l.locale}</span>
              <span className={l.completeness_pct === 100 ? "text-green-600" : "text-yellow-600"}>
                {l.completeness_pct}% {l.completeness_pct === 100 ? "✅" : `(${l.missing_count} missing)`}
              </span>
            </div>
            <div className="mt-1 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${l.completeness_pct === 100 ? "bg-green-500" : "bg-yellow-500"}`}
                style={{ width: `${l.completeness_pct}%` }} />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
