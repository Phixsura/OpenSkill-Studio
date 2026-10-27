"use client";

interface PeerReputation {
  total_envelopes: number;
  invalid_signature_rate: number;
  spam_score: number;
}

interface FederationPeer {
  id: string;
  instance_uri: string;
  display_name: string;
  description: string | null;
  logo_url: string | null;
  protocol_version: string;
  trust_status: "pending" | "trusted" | "suspended" | "revoked";
  last_seen_at: string | null;
  reputation: PeerReputation | null;
}

interface FederationPeerCardProps {
  peer: FederationPeer;
  onTrust: (id: string) => void;
  onSuspend: (id: string) => void;
  onRevoke: (id: string) => void;
  onRemove: (id: string) => void;
}

const TRUST_CONFIG: Record<string, { label: string; color: string; dot: string }> = {
  trusted: {
    label: "Trusted",
    color: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    dot: "bg-green-500",
  },
  pending: {
    label: "Pending",
    color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
    dot: "bg-yellow-500",
  },
  suspended: {
    label: "Suspended",
    color: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300",
    dot: "bg-orange-500",
  },
  revoked: {
    label: "Revoked",
    color: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
    dot: "bg-red-500",
  },
};

function TrustBadge({ status }: { status: string }) {
  const config = TRUST_CONFIG[status] ?? TRUST_CONFIG.pending;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${config.color}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  );
}

function ReputationBar({
  label,
  value,
  max,
  warn,
}: {
  label: string;
  value: number;
  max: number;
  warn: number;
}) {
  const pct = Math.min((value / max) * 100, 100);
  const isWarn = value >= warn;
  return (
    <div className="space-y-0.5">
      <div className="flex justify-between text-xs">
        <span className="text-gray-500">{label}</span>
        <span className={isWarn ? "font-medium text-red-600" : "text-gray-600 dark:text-gray-400"}>
          {typeof value === "number" && value < 1
            ? `${(value * 100).toFixed(1)}%`
            : value.toLocaleString()}
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className={`h-full rounded-full transition-all ${isWarn ? "bg-red-500" : "bg-blue-500"}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function formatLastSeen(iso: string | null): string {
  if (!iso) return "Never";
  try {
    const d = new Date(iso);
    const diff = Date.now() - d.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  } catch {
    return iso;
  }
}

export function FederationPeerCard({
  peer,
  onTrust,
  onSuspend,
  onRevoke,
  onRemove,
}: FederationPeerCardProps) {
  return (
    <div
      className="rounded-xl border border-gray-200 p-4 dark:border-gray-700"
      data-testid="peer-card"
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          {peer.logo_url ? (
            <img src={peer.logo_url} alt="" className="h-10 w-10 rounded-lg object-cover" />
          ) : (
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 text-lg dark:bg-blue-900/30">
              🌐
            </div>
          )}
          <div>
            <h3 className="font-semibold">{peer.display_name}</h3>
            <p className="font-mono text-xs text-gray-400">{peer.instance_uri}</p>
          </div>
        </div>
        <TrustBadge status={peer.trust_status} />
      </div>

      {/* Description */}
      {peer.description && (
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{peer.description}</p>
      )}

      {/* Meta row */}
      <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
        <span>Protocol v{peer.protocol_version}</span>
        <span>Last seen: {formatLastSeen(peer.last_seen_at)}</span>
      </div>

      {/* Reputation */}
      {peer.reputation && (
        <div className="mt-3 space-y-2">
          <p className="text-xs font-medium text-gray-500">Reputation</p>
          <ReputationBar
            label="Envelopes"
            value={peer.reputation.total_envelopes}
            max={10000}
            warn={0}
          />
          <ReputationBar
            label="Invalid sig rate"
            value={peer.reputation.invalid_signature_rate}
            max={0.1}
            warn={0.05}
          />
          <ReputationBar
            label="Spam score"
            value={peer.reputation.spam_score}
            max={1.0}
            warn={0.8}
          />
        </div>
      )}

      {/* Actions */}
      <div className="mt-4 flex gap-2 border-t border-gray-100 pt-3 dark:border-gray-800">
        {peer.trust_status === "pending" && (
          <button
            onClick={() => onTrust(peer.id)}
            className="rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700"
          >
            Trust
          </button>
        )}
        {peer.trust_status === "trusted" && (
          <button
            onClick={() => onSuspend(peer.id)}
            className="rounded-md border border-orange-300 px-3 py-1.5 text-xs font-medium text-orange-600 hover:bg-orange-50 dark:border-orange-700 dark:text-orange-400 dark:hover:bg-orange-900/20"
          >
            Suspend
          </button>
        )}
        {(peer.trust_status === "suspended" || peer.trust_status === "pending") && (
          <button
            onClick={() => onRevoke(peer.id)}
            className="rounded-md border border-red-300 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 dark:border-red-700 dark:text-red-400 dark:hover:bg-red-900/20"
          >
            Revoke
          </button>
        )}
        <button
          onClick={() => onRemove(peer.id)}
          className="ml-auto rounded-md border border-gray-300 px-3 py-1.5 text-xs text-gray-500 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-800"
        >
          Remove
        </button>
      </div>
    </div>
  );
}
