"use client";

interface SampleInfo {
  sample_id: string;
  method: string;
  path: string;
  status_code: number;
  duration_ms: number;
  timestamp: string;
}

interface RequestSamplerCardProps {
  samples: SampleInfo[];
  sampleRate: number;
  totalSamples: number;
  appName: string;
}

const METHOD_COLORS: Record<string, string> = {
  GET: "text-green-700 bg-green-100 dark:text-green-400 dark:bg-green-900/30",
  POST: "text-blue-700 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30",
  PUT: "text-yellow-700 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30",
  DELETE: "text-red-700 bg-red-100 dark:text-red-400 dark:bg-red-900/30",
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  return `${Math.floor(diff / 3_600_000)}h ago`;
}

export default function RequestSamplerCard({
  samples,
  sampleRate,
  totalSamples,
  appName,
}: RequestSamplerCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Request Sampler
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>{(sampleRate * 100).toFixed(0)}% rate</span>
          <span>· {totalSamples} stored</span>
        </div>
      </div>

      {samples.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No samples captured</p>
      ) : (
        <div className="space-y-1">
          {samples.map((s) => (
            <div
              key={s.sample_id}
              className="flex items-center justify-between rounded px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`rounded px-1 py-0.5 text-[9px] font-bold ${METHOD_COLORS[s.method] ?? "bg-gray-100 text-gray-600"}`}
                >
                  {s.method}
                </span>
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{s.path}</span>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-gray-400">
                <span className={s.status_code >= 400 ? "text-red-500" : ""}>{s.status_code}</span>
                <span>{s.duration_ms.toFixed(0)}ms</span>
                <span>{timeAgo(s.timestamp)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
