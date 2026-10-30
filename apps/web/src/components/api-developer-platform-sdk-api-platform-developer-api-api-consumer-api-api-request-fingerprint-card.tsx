"use client";

interface FpInfo { fingerprint_id: string; method: string; path: string; hit_count: number; }
interface Props { fingerprints: FpInfo[]; uniqueCount: number; dedupRatio: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestFingerprintCard({ fingerprints, uniqueCount, dedupRatio, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔏 Request Fingerprints</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {uniqueCount} unique</p>
        </div>
        <span className="text-[10px] text-gray-400">{dedupRatio}% dedup</span>
      </div>
      {fingerprints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No fingerprints</p>
      ) : (
        <div className="space-y-1">
          {fingerprints.map((f) => (
            <div key={f.fingerprint_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{f.method} {f.path}</span>
              <span className="text-gray-400">{f.hit_count.toLocaleString()}×</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
