"use client";

interface DigestInfo {
  digest_id: string;
  period: string;
  period_label: string;
  entry_count: number;
  delivered: boolean;
}

interface APIChangelogDigestCardProps {
  digests: DigestInfo[];
  appName: string;
}

export default function APIChangelogDigestCard({ digests, appName }: APIChangelogDigestCardProps) {
  const delivered = digests.filter((d) => d.delivered).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📨 Changelog Digests</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{delivered}/{digests.length} delivered</span>
      </div>

      {digests.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No digests</p>
      ) : (
        <div className="space-y-1.5">
          {digests.map((d) => (
            <div key={d.digest_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${d.delivered ? "bg-green-500" : "bg-gray-400"}`} />
                <span className="text-xs text-gray-700 dark:text-gray-300">{d.period_label}</span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{d.period}</span>
              </div>
              <span className="text-[10px] text-gray-400">{d.entry_count} entries</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
