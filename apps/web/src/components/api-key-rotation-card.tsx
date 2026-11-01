"use client";

interface APIKeyInfo {
  key_id: string;
  prefix: string;
  label: string;
  is_active: boolean;
  revoked: boolean;
  is_expired: boolean;
  created_at: number;
}

interface APIKeyRotationCardProps {
  keys: APIKeyInfo[];
  appName: string;
}

export default function APIKeyRotationCard({ keys, appName }: APIKeyRotationCardProps) {
  const active = keys.filter((k) => k.is_active).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔑 API Key Rotation
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {active} active / {keys.length} total
        </span>
      </div>

      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No API keys</p>
      ) : (
        <div className="space-y-1.5">
          {keys.map((k) => (
            <div
              key={k.key_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                    {k.prefix}...
                  </span>
                  {k.label && <span className="text-[11px] text-gray-500">{k.label}</span>}
                </div>
              </div>
              <span
                className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                  k.revoked
                    ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                    : k.is_expired
                      ? "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
                      : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                }`}
              >
                {k.revoked ? "revoked" : k.is_expired ? "expired" : "active"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
