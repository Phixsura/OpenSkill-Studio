"use client";

interface PendingInvite { email: string; role: string; status: string; }
interface PendingInvitesListProps { invites: PendingInvite[];
  onResend: (email: string) => void; onRevoke: (email: string) => void; }

export function PendingInvitesList({ invites, onResend, onRevoke }: PendingInvitesListProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">✉️ Pending Invites</h3>
        <span className="text-xs text-gray-400">{invites.length} pending</span>
      </div>
      <div className="space-y-2">
        {invites.map(inv => (
          <div key={inv.email} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <p className="text-sm">{inv.email}</p>
              <span className="text-xs text-gray-400 capitalize">{inv.role}</span>
            </div>
            <div className="flex gap-2">
              <button onClick={() => onResend(inv.email)}
                className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Resend</button>
              <button onClick={() => onRevoke(inv.email)}
                className="text-xs px-2 py-1 text-red-500 border border-red-200 rounded hover:bg-red-50">Revoke</button>
            </div>
          </div>
        ))}
        {invites.length === 0 && <p className="text-sm text-gray-400 text-center">No pending invites</p>}
      </div>
    </div>
  );
}
