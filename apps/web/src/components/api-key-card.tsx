"use client";

interface ApiKeyInfo {
  key_id: string;
  name: string;
  prefix: string;
  scopes: string[];
  created_at: string;
  expires_at: string | null;
  revoked: boolean;
  last_used_at: string | null;
}

interface ApiKeyCardProps {
  keys: ApiKeyInfo[];
  appName: string;
}

function timeAgo(iso: string | null): string {
  if (!iso) return "Never";
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

function isExpired(expiresAt: string | null): boolean {
  if (!expiresAt) return false;
  return new Date(expiresAt).getTime() < Date.now();
}

export default function ApiKeyCard({ keys, appName }: ApiKeyCardProps) {
  const activeCount = keys.filter((k) => !k.revoked && !isExpired(k.expires_at)).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">API Keys</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{activeCount} active</span>
      </div>

      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No API keys</p>
      ) : (
        <div className="space-y-2.5">
          {keys.map((k) => {
            const expired = isExpired(k.expires_at);
            const inactive = k.revoked || expired;
            return (
              <div
                key={k.key_id}
                className={`rounded-lg border px-3 py-2.5 ${
                  inactive
                    ? "border-gray-100 bg-gray-50 opacity-60 dark:border-gray-800 dark:bg-gray-800/50"
                    : "border-gray-100 dark:border-gray-800"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                      {k.name}
                    </span>
                    {k.revoked && (
                      <span className="rounded bg-red-100 px-1.5 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
                        Revoked
                      </span>
                    )}
                    {expired && !k.revoked && (
                      <span className="rounded bg-yellow-100 px-1.5 py-0.5 text-[10px] font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
                        Expired
                      </span>
                    )}
                  </div>
                  <span className="font-mono text-xs text-gray-400">{k.prefix}••••••••</span>
                </div>
                <div className="mt-1.5 flex items-center gap-3">
                  {k.scopes.length > 0 ? (
                    <div className="flex flex-wrap gap-1">
                      {k.scopes.map((s) => (
                        <span
                          key={s}
                          className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-[11px] text-gray-400">No scopes</span>
                  )}
                </div>
                <div className="mt-1 flex items-center justify-between text-[11px] text-gray-400">
                  <span>Last used: {timeAgo(k.last_used_at)}</span>
                  {k.expires_at && (
                    <span>
                      {expired ? "Expired" : "Expires"}:{" "}
                      {new Date(k.expires_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
