"use client";

interface AllowlistEntryInfo {
  entry_id: string;
  cidr: string;
  label: string;
  is_expired: boolean;
}

interface IPAllowlistCardProps {
  entries: AllowlistEntryInfo[];
  appName: string;
}

export default function IPAllowlistCard({ entries, appName }: IPAllowlistCardProps) {
  const active = entries.filter((e) => !e.is_expired).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🛡️ IP Allowlist
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{active} active rules</span>
      </div>

      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No IP rules — all denied</p>
      ) : (
        <div className="space-y-1.5">
          {entries.map((e) => (
            <div
              key={e.entry_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2 w-2 rounded-full ${e.is_expired ? "bg-gray-400" : "bg-green-500"}`}
                />
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{e.cidr}</span>
                {e.label && <span className="text-[11px] text-gray-500">{e.label}</span>}
              </div>
              {e.is_expired && (
                <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-500 dark:bg-gray-800">
                  expired
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
