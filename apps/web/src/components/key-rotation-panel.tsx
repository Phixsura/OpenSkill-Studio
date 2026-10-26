"use client";

interface ApiKeyInfo {
  keyId: string;
  status: "active" | "grace" | "revoked";
  createdAt: string;
  expiresIn?: string;
}

interface RotationEvent {
  oldKeyId: string;
  newKeyId: string;
  reason: string;
  timestamp: string;
}

const statusConfig: Record<string, { color: string; icon: string }> = {
  active: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "🟢" },
  grace: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⏳" },
  revoked: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "🚫" },
};

export function KeyRotationPanel({
  keys,
  history,
  extensionName,
  onRotate,
  onRevoke,
}: {
  keys: ApiKeyInfo[];
  history: RotationEvent[];
  extensionName: string;
  onRotate?: () => void;
  onRevoke?: (keyId: string) => void;
}) {
  const active = keys.filter((k) => k.status === "active").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔄 {extensionName} Key Rotation</h2>
        <button onClick={onRotate} className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">Rotate Now</button>
      </div>

      <div className="space-y-1">
        {keys.map((key) => {
          const cfg = statusConfig[key.status];
          return (
            <div key={key.keyId} className={`rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between ${key.status === "revoked" ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-2">
                <span>{cfg.icon}</span>
                <code className="text-sm">{key.keyId}</code>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{key.status}</span>
                {key.expiresIn && <span className="text-xs text-gray-400">expires {key.expiresIn}</span>}
              </div>
              {key.status !== "revoked" && (
                <button onClick={() => onRevoke?.(key.keyId)}
                  className="text-xs bg-red-600 text-white px-2 py-1 rounded">Revoke</button>
              )}
            </div>
          );
        })}
      </div>

      {history.length > 0 && (
        <div>
          <span className="text-sm font-semibold">Rotation History</span>
          <div className="mt-1 space-y-1">
            {history.map((evt, i) => (
              <div key={i} className="text-xs text-gray-500 flex gap-2">
                <span>{evt.timestamp}</span>
                <span>{evt.oldKeyId} → {evt.newKeyId}</span>
                <span className="text-gray-400">({evt.reason})</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
