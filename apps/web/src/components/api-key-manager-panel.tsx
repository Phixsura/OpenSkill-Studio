"use client";

interface ApiKeyRecord {
  key_id: string;
  key_prefix: string;
  scopes: string[];
  status: "active" | "expired" | "revoked" | "rotated";
  created_at: string;
  expires_at: string | null;
  last_used_at: string | null;
}

interface ApiKeyManagerPanelProps {
  installationId: string;
  keys: ApiKeyRecord[];
  onCreateKey: () => void;
  onRevokeKey: (keyId: string) => void;
  onRotateKey: (keyId: string) => void;
}

const STATUS_STYLES: Record<string, { label: string; color: string }> = {
  active: {
    label: "Active",
    color: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300",
  },
  expired: {
    label: "Expired",
    color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  },
  revoked: {
    label: "Revoked",
    color: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300",
  },
  rotated: {
    label: "Rotated",
    color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300",
  },
};

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

function timeAgo(iso: string | null): string {
  if (!iso) return "Never";
  try {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  } catch {
    return iso;
  }
}

export function ApiKeyManagerPanel({
  keys,
  onCreateKey,
  onRevokeKey,
  onRotateKey,
}: ApiKeyManagerPanelProps) {
  const activeCount = keys.filter((k) => k.status === "active").length;

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div>
          <h3 className="font-semibold">API Keys</h3>
          <p className="text-xs text-gray-500">
            {keys.length} keys • {activeCount} active
          </p>
        </div>
        <button
          onClick={onCreateKey}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
        >
          + New Key
        </button>
      </div>

      {keys.length === 0 ? (
        <div className="py-8 text-center">
          <span className="text-3xl">🔑</span>
          <p className="mt-2 text-sm text-gray-500">No API keys yet</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {keys.map((k) => {
            const st = STATUS_STYLES[k.status] ?? STATUS_STYLES.revoked;
            return (
              <div key={k.key_id} className="px-4 py-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <code className="text-xs font-medium">{k.key_prefix}</code>
                    <span className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${st.color}`}>
                      {st.label}
                    </span>
                  </div>
                  <div className="flex gap-1">
                    {k.status === "active" && (
                      <>
                        <button
                          onClick={() => onRotateKey(k.key_id)}
                          className="rounded border border-blue-300 px-2 py-0.5 text-[10px] text-blue-600 hover:bg-blue-50 dark:border-blue-700 dark:text-blue-400"
                        >
                          Rotate
                        </button>
                        <button
                          onClick={() => onRevokeKey(k.key_id)}
                          className="rounded border border-red-300 px-2 py-0.5 text-[10px] text-red-600 hover:bg-red-50 dark:border-red-700 dark:text-red-400"
                        >
                          Revoke
                        </button>
                      </>
                    )}
                  </div>
                </div>
                <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                  <span>Created {formatDate(k.created_at)}</span>
                  <span>Last used: {timeAgo(k.last_used_at)}</span>
                  {k.expires_at && <span>Expires {formatDate(k.expires_at)}</span>}
                </div>
                <div className="mt-1 flex gap-1">
                  {k.scopes.slice(0, 4).map((s) => (
                    <code
                      key={s}
                      className="rounded bg-gray-100 px-1 py-0.5 text-[9px] dark:bg-gray-800"
                    >
                      {s}
                    </code>
                  ))}
                  {k.scopes.length > 4 && (
                    <span className="text-[9px] text-gray-400">+{k.scopes.length - 4} more</span>
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
