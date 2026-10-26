"use client";

interface SandboxBoundary {
  sandboxId: string;
  tenantId: string;
  isolationLevel: "shared" | "namespace" | "full";
  namespace: string;
  commPolicy: "deny_all" | "allow_same_tenant" | "allow_explicit";
  allowedPeers: string[];
  sharedVolumes: string[];
}

const levelConfig: Record<string, { color: string; icon: string; label: string }> = {
  shared: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "🔓", label: "Shared" },
  namespace: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", icon: "📦", label: "Namespace" },
  full: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "🔒", label: "Full" },
};

const policyLabels: Record<string, string> = {
  deny_all: "🚫 Deny All", allow_same_tenant: "🏢 Same Tenant", allow_explicit: "✅ Explicit",
};

export function IsolationBoundaryPanel({
  boundaries,
  currentSandbox,
  onAllowPeer,
  onCheckComm,
}: {
  boundaries: SandboxBoundary[];
  currentSandbox: string;
  onAllowPeer?: (peerId: string) => void;
  onCheckComm?: (targetId: string) => void;
}) {
  const current = boundaries.find((b) => b.sandboxId === currentSandbox);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔐 Isolation Boundaries</h2>

      {current && (
        <div className="rounded-xl border-2 border-blue-400 dark:border-blue-600 p-4 space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold">Current: {current.sandboxId}</span>
            {(() => { const cfg = levelConfig[current.isolationLevel]; return (
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{cfg.icon} {cfg.label}</span>
            ); })()}
          </div>
          <div className="text-xs text-gray-500 space-y-0.5">
            <div>Tenant: <code>{current.tenantId}</code></div>
            <div>Namespace: <code>{current.namespace}</code></div>
            <div>Policy: {policyLabels[current.commPolicy]}</div>
            {current.allowedPeers.length > 0 && (
              <div>Peers: {current.allowedPeers.join(", ")}</div>
            )}
            {current.sharedVolumes.length > 0 && (
              <div>Volumes: {current.sharedVolumes.join(", ")}</div>
            )}
          </div>
        </div>
      )}

      <div className="space-y-1">
        {boundaries.filter((b) => b.sandboxId !== currentSandbox).map((b) => {
          const cfg = levelConfig[b.isolationLevel];
          return (
            <div key={b.sandboxId} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span>{cfg.icon}</span>
                <code className="text-sm">{b.sandboxId}</code>
                <span className="text-xs text-gray-400">{b.tenantId}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{cfg.label}</span>
              </div>
              <div className="flex gap-1">
                <button onClick={() => onCheckComm?.(b.sandboxId)}
                  className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Check</button>
                <button onClick={() => onAllowPeer?.(b.sandboxId)}
                  className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Allow</button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
