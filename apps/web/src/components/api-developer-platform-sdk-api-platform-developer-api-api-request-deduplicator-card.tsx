"use client";

interface Stats { total_fingerprints: number; duplicates_detected: number; }
interface Props { stats: Stats; windowSeconds: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestDeduplicatorCard({ stats, windowSeconds, appName }: Props) {
  const dupeRate = stats.total_fingerprints > 0 ? ((stats.duplicates_detected / stats.total_fingerprints) * 100).toFixed(1) : "0.0";
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Deduplicator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {windowSeconds}s window</p>
        </div>
        <span className="text-[10px] text-gray-400">{dupeRate}% dupes</span>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.total_fingerprints.toLocaleString()}</div><div className="text-gray-400">Fingerprints</div></div>
        <div><div className="font-semibold text-amber-600 dark:text-amber-400">{stats.duplicates_detected}</div><div className="text-gray-400">Duplicates</div></div>
      </div>
    </div>
  );
}
