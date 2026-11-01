"use client";

interface SampleInfo { sample_id: string; endpoint: string; language: string; title: string; copy_count: number; }
interface Props { samples: SampleInfo[]; appName: string; }

const langColor: Record<string, string> = { python: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300", javascript: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300", go: "bg-cyan-100 text-cyan-700 dark:bg-cyan-900 dark:text-cyan-300", ruby: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300" };

export default function APIDeveloperCodeSampleCard({ samples, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💻 Code Samples</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{samples.length} samples</span>
      </div>
      {samples.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No code samples</p>
      ) : (
        <div className="space-y-1">
          {samples.map((s) => (
            <div key={s.sample_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1 py-0.5 text-[9px] font-medium ${langColor[s.language] ?? "bg-gray-100 text-gray-600 dark:bg-gray-800"}`}>{s.language}</span>
                <span className="text-gray-700 dark:text-gray-300">{s.title || s.endpoint}</span>
              </div>
              <span className="text-gray-400">{s.copy_count} copies</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
