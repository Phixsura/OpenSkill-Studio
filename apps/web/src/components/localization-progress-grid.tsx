"use client";

interface LocaleStatus { locale: string; language: string; completed_fields: number; total_fields: number; progress: number; is_default: boolean; }
interface LocalizationProgressGridProps { locales: LocaleStatus[]; overallProgress: number; }

export function LocalizationProgressGrid({ locales, overallProgress }: LocalizationProgressGridProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Localization</h2>
        <span className="text-sm text-gray-500">Overall: <strong>{overallProgress}%</strong></span>
      </div>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        {locales.map(l => (
          <div key={l.locale} className={`rounded-lg border p-3 ${l.is_default ? "border-blue-300 dark:border-blue-700" : "border-gray-200 dark:border-gray-700"}`}>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{l.language}</span>
              <span className="font-mono text-xs text-gray-400">{l.locale}</span>
            </div>
            <div className="mt-2 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${l.progress === 100 ? "bg-green-500" : l.progress > 0 ? "bg-yellow-500" : "bg-gray-300 dark:bg-gray-600"}`}
                style={{ width: `${l.progress}%` }} />
            </div>
            <p className="mt-1 text-xs text-gray-400">{l.completed_fields}/{l.total_fields} fields</p>
          </div>
        ))}
      </div>
    </div>
  );
}
