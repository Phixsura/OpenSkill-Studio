"use client";

interface SampleInfo { sample_id: string; title: string; language: string; endpoint: string; views: number; copies: number; }
interface Props { samples: SampleInfo[]; languageCounts: Record<string, number>; appName: string; }

const langColor: Record<string, string> = { python: "bg-blue-100 text-blue-700", javascript: "bg-yellow-100 text-yellow-700", typescript: "bg-blue-100 text-blue-700", go: "bg-cyan-100 text-cyan-700", ruby: "bg-red-100 text-red-700", java: "bg-orange-100 text-orange-700", curl: "bg-gray-100 text-gray-700" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiCodeSampleLibraryCard({ samples, languageCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💻 Code Samples</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {samples.length} samples</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(languageCounts).map(([lang, count]) => (
          <span key={lang} className={`rounded px-1.5 py-0.5 text-[10px] ${langColor[lang] ?? "bg-gray-100 text-gray-600"}`}>{lang}: {count}</span>
        ))}
      </div>
      {samples.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No code samples</p>
      ) : (
        <div className="space-y-1.5">
          {samples.slice(0, 5).map((s) => (
            <div key={s.sample_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1 py-0.5 text-[9px] ${langColor[s.language] ?? ""}`}>{s.language}</span>
                <span className="text-gray-700 dark:text-gray-300">{s.title}</span>
              </div>
              <span className="text-gray-400">{s.views} views · {s.copies} copies</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
