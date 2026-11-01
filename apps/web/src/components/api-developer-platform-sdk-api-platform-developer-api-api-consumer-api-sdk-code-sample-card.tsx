"use client";

interface SampleInfo { sample_id: string; endpoint: string; method: string; language: string; }
interface Props { samples: SampleInfo[]; totalSamples: number; languages: string[]; appName: string; }

const langIcon: Record<string, string> = { python: "🐍", typescript: "📘", javascript: "📒", curl: "🌀", go: "🔵", ruby: "💎", java: "☕", csharp: "🟣", php: "🐘" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiSdkCodeSampleCard({ samples, totalSamples, languages, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💻 Code Samples</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalSamples} samples</p>
        </div>
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {languages.map((l) => <span key={l} className="rounded bg-gray-100 px-1.5 py-0.5 text-[9px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">{langIcon[l] ?? "•"} {l}</span>)}
      </div>
      {samples.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No code samples</p>
      ) : (
        <div className="space-y-1">
          {samples.map((s) => (
            <div key={s.sample_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.method} {s.endpoint}</span>
              <span className="text-gray-400">{langIcon[s.language] ?? ""} {s.language}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
