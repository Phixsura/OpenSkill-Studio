"use client";

interface Invite { email: string; role: string; inviter: string; status: string; expiresAt: string; }
interface InviteListProps { invites: Invite[]; onRevoke: (email: string) => void; onResend: (email: string) => void; }

const statusBadge: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  accepted: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  expired: "bg-gray-100 text-gray-500 dark:bg-gray-800",
};

export function InviteList({ invites, onRevoke, onResend }: InviteListProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Team Invitations</h3>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {invites.map(inv => (
          <div key={inv.email} className="flex items-center justify-between px-4 py-3">
            <div>
              <p className="text-sm font-medium">{inv.email}</p>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-xs text-gray-400 capitalize">{inv.role}</span>
                <span className={`rounded px-1.5 py-0.5 text-xs ${statusBadge[inv.status] ?? ""}`}>{inv.status}</span>
              </div>
            </div>
            <div className="flex gap-2">
              {inv.status === "pending" && (
                <>
                  <button onClick={() => onResend(inv.email)} className="text-xs text-blue-600 hover:underline">Resend</button>
                  <button onClick={() => onRevoke(inv.email)} className="text-xs text-red-600 hover:underline">Revoke</button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
