"use client";

interface InviteInfo {
  invite_id: string;
  email: string;
  role: string;
  status: "pending" | "accepted" | "declined" | "revoked" | "expired";
  created_at: string;
}

interface InviteManagerCardProps {
  invites: InviteInfo[];
  appName: string;
}

const STATUS_STYLES: Record<string, { icon: string; text: string }> = {
  pending: { icon: "📧", text: "text-blue-600 dark:text-blue-400" },
  accepted: { icon: "✅", text: "text-green-600 dark:text-green-400" },
  declined: { icon: "❌", text: "text-red-500" },
  revoked: { icon: "🚫", text: "text-gray-400" },
  expired: { icon: "🕐", text: "text-gray-400" },
};

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function InviteManagerCard({ invites, appName }: InviteManagerCardProps) {
  const pendingCount = invites.filter((i) => i.status === "pending").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Invitations</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {pendingCount > 0 && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
            {pendingCount} pending
          </span>
        )}
      </div>

      {invites.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No invitations</p>
      ) : (
        <div className="space-y-1.5">
          {invites.map((inv) => {
            const st = STATUS_STYLES[inv.status] ?? STATUS_STYLES.pending;
            return (
              <div
                key={inv.invite_id}
                className={`flex items-center justify-between rounded px-2.5 py-2 ${inv.status === "pending" ? "bg-blue-50/50 dark:bg-blue-950/10" : ""}`}
              >
                <div className="flex items-center gap-2">
                  <span>{st.icon}</span>
                  <div>
                    <span className="text-sm text-gray-800 dark:text-gray-200">{inv.email}</span>
                    <div className="flex items-center gap-2 text-[11px] text-gray-400">
                      <span className="capitalize">{inv.role}</span>
                      <span>·</span>
                      <span>{timeAgo(inv.created_at)}</span>
                    </div>
                  </div>
                </div>
                <span className={`text-xs font-medium capitalize ${st.text}`}>{inv.status}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
