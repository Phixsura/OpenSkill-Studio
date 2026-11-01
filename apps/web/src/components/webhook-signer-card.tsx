"use client";

interface SigningSecretInfo {
  secret_id: string;
  prefix: string;
  active: boolean;
  created_at: string;
}

interface WebhookSignerCardProps {
  secrets: SigningSecretInfo[];
  appName: string;
  toleranceSeconds: number;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function WebhookSignerCard({
  secrets: secs,
  appName,
  toleranceSeconds,
}: WebhookSignerCardProps) {
  const activeCount = secs.filter((s) => s.active).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Webhook Signing
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">
            HMAC-SHA256
          </span>
          <span className="text-[11px] text-gray-400">{toleranceSeconds}s window</span>
        </div>
      </div>

      {secs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No signing secrets</p>
      ) : (
        <div className="space-y-2">
          {secs.map((sec) => (
            <div
              key={sec.secret_id}
              className={`flex items-center justify-between rounded-lg border px-3 py-2.5 ${
                sec.active
                  ? "border-gray-100 dark:border-gray-800"
                  : "border-gray-100 bg-gray-50 opacity-60 dark:border-gray-800 dark:bg-gray-800/50"
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2.5 w-2.5 rounded-full ${
                    sec.active ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"
                  }`}
                />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                      {sec.secret_id}
                    </span>
                    {!sec.active && <span className="text-[10px] text-gray-400">revoked</span>}
                  </div>
                  <span className="font-mono text-[11px] text-gray-400">{sec.prefix}••••••••</span>
                </div>
              </div>
              <span className="text-[11px] text-gray-400">Created {timeAgo(sec.created_at)}</span>
            </div>
          ))}
          <div className="mt-2 text-center text-[11px] text-gray-400">
            {activeCount} active secret{activeCount !== 1 ? "s" : ""}
          </div>
        </div>
      )}
    </div>
  );
}
