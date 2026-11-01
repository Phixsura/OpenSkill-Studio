"use client";

interface ChannelRelease {
  version: string;
  published_at: string;
  notes: string;
}

interface ChannelData {
  channel: "stable" | "beta" | "canary" | "internal";
  latest_version: string | null;
  history: ChannelRelease[];
}

interface ReleaseChannelPanelProps {
  appName: string;
  channels: ChannelData[];
  currentSubscription: string | null;
  pinnedVersion: string | null;
  onPromote: (from: string, to: string) => void;
  onRollback: (channel: string) => void;
  onSubscribe: (channel: string) => void;
}

const CH_STYLES: Record<string, { color: string; bg: string; icon: string }> = {
  stable: {
    color: "text-green-700 dark:text-green-300",
    bg: "bg-green-100 dark:bg-green-900/20",
    icon: "✓",
  },
  beta: {
    color: "text-blue-700 dark:text-blue-300",
    bg: "bg-blue-100 dark:bg-blue-900/20",
    icon: "β",
  },
  canary: {
    color: "text-yellow-700 dark:text-yellow-300",
    bg: "bg-yellow-100 dark:bg-yellow-900/20",
    icon: "🐤",
  },
  internal: {
    color: "text-gray-600 dark:text-gray-400",
    bg: "bg-gray-100 dark:bg-gray-800",
    icon: "🔒",
  },
};

const PROMOTE_TARGETS: Record<string, string> = {
  internal: "canary",
  canary: "beta",
  beta: "stable",
};

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric" });
  } catch {
    return iso;
  }
}

export function ReleaseChannelPanel({
  appName,
  channels,
  currentSubscription,
  pinnedVersion,
  onPromote,
  onRollback,
  onSubscribe,
}: ReleaseChannelPanelProps) {
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <h3 className="font-semibold">Release Channels</h3>
        <p className="text-xs text-gray-500">
          {appName}
          {currentSubscription && (
            <span>
              {" "}
              • Subscribed to <strong>{currentSubscription}</strong>
            </span>
          )}
          {pinnedVersion && <span> • Pinned: {pinnedVersion}</span>}
        </p>
      </div>

      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {channels.map((ch) => {
          const style = CH_STYLES[ch.channel] ?? CH_STYLES.internal;
          const promoteTo = PROMOTE_TARGETS[ch.channel];
          const isSubscribed = currentSubscription === ch.channel;

          return (
            <div key={ch.channel} className="px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${style.color} ${style.bg}`}
                  >
                    {style.icon} {ch.channel}
                  </span>
                  {ch.latest_version ? (
                    <code className="text-xs font-medium">{ch.latest_version}</code>
                  ) : (
                    <span className="text-xs text-gray-400">No releases</span>
                  )}
                  {isSubscribed && (
                    <span className="rounded bg-blue-500 px-1 py-0.5 text-[9px] font-bold text-white">
                      SUBSCRIBED
                    </span>
                  )}
                </div>
                <div className="flex gap-1">
                  {!isSubscribed && (
                    <button
                      onClick={() => onSubscribe(ch.channel)}
                      className="rounded border border-gray-300 px-2 py-0.5 text-[10px] hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-800"
                    >
                      Subscribe
                    </button>
                  )}
                  {promoteTo && ch.latest_version && (
                    <button
                      onClick={() => onPromote(ch.channel, promoteTo)}
                      className="rounded border border-blue-300 px-2 py-0.5 text-[10px] text-blue-600 hover:bg-blue-50 dark:border-blue-700 dark:text-blue-400"
                    >
                      → {promoteTo}
                    </button>
                  )}
                  {ch.history.length >= 2 && (
                    <button
                      onClick={() => onRollback(ch.channel)}
                      className="rounded border border-orange-300 px-2 py-0.5 text-[10px] text-orange-600 hover:bg-orange-50 dark:border-orange-700 dark:text-orange-400"
                    >
                      Rollback
                    </button>
                  )}
                </div>
              </div>

              {ch.history.length > 0 && (
                <div className="mt-1.5 space-y-0.5">
                  {ch.history.slice(0, 3).map((r) => (
                    <div
                      key={r.version}
                      className="flex items-center gap-2 text-[10px] text-gray-500"
                    >
                      <code>{r.version}</code>
                      <span>{formatDate(r.published_at)}</span>
                      {r.notes && <span className="truncate text-gray-400">— {r.notes}</span>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
