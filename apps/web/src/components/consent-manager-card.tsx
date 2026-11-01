"use client";

interface ConsentStatus {
  purpose: string;
  granted: boolean;
  last_updated: string;
}

interface ConsentManagerCardProps {
  consents: ConsentStatus[];
  userId: string;
  appName: string;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function ConsentManagerCard({ consents, userId, appName }: ConsentManagerCardProps) {
  const grantedCount = consents.filter((c) => c.granted).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Consent</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {userId}
          </p>
        </div>
        <span className="text-xs text-gray-400">
          {grantedCount}/{consents.length} granted
        </span>
      </div>

      {consents.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No consent records</p>
      ) : (
        <div className="space-y-2">
          {consents.map((c) => (
            <div
              key={c.purpose}
              className="flex items-center justify-between rounded px-2.5 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2.5">
                <span
                  className={`h-3 w-3 rounded-full ${c.granted ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"}`}
                />
                <div>
                  <span className="text-sm capitalize text-gray-800 dark:text-gray-200">
                    {c.purpose.replace(/_/g, " ")}
                  </span>
                  <p className="text-[11px] text-gray-400">Updated {timeAgo(c.last_updated)}</p>
                </div>
              </div>
              <span
                className={`text-xs font-medium ${c.granted ? "text-green-600 dark:text-green-400" : "text-gray-400"}`}
              >
                {c.granted ? "Granted" : "Withdrawn"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
