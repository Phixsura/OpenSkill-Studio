"use client";

interface DNSRecordInfo {
  hostname: string;
  addresses: string[];
  ttl_seconds: number;
  lookup_ms: number;
  failed: boolean;
  error: string;
}

interface DNSResolverCardProps {
  records: DNSRecordInfo[];
  appName: string;
}

export default function DNSResolverCard({ records, appName }: DNSResolverCardProps) {
  const failedCount = records.filter((r) => r.failed).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">DNS Resolver</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{records.length} cached</span>
          {failedCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {failedCount} failed
            </span>
          )}
        </div>
      </div>

      {records.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No DNS records cached</p>
      ) : (
        <div className="space-y-1.5">
          {records.map((r) => (
            <div
              key={r.hostname}
              className={`flex items-center justify-between rounded px-2.5 py-1.5 ${
                r.failed
                  ? "bg-red-50/50 dark:bg-red-950/10"
                  : "hover:bg-gray-50 dark:hover:bg-gray-800/50"
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2 w-2 rounded-full ${r.failed ? "bg-red-500" : "bg-green-500"}`}
                />
                <div>
                  <span className="font-mono text-xs text-gray-800 dark:text-gray-200">
                    {r.hostname}
                  </span>
                  {r.failed ? (
                    <p className="text-[10px] text-red-500">{r.error}</p>
                  ) : (
                    <p className="text-[10px] text-gray-400">{r.addresses.join(", ")}</p>
                  )}
                </div>
              </div>
              <div className="text-[11px] text-gray-400">
                {!r.failed && (
                  <span>
                    {r.lookup_ms.toFixed(0)}ms · TTL {r.ttl_seconds}s
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
