"use client";

interface Member { id: string; name: string; email: string; role: string;
  roleIcon: string; active: boolean; }
interface Invite { email: string; role: string; sentAt: string; }
interface TeamPageProps { orgName: string; members: Member[]; pendingInvites: Invite[];
  onRemove: (id: string) => void; onInvite: () => void; onRevokeInvite: (email: string) => void; }

export function TeamPage({ orgName, members, pendingInvites, onRemove, onInvite, onRevokeInvite }: TeamPageProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">👥 {orgName} Team</h2>
        <button onClick={onInvite} className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white">+ Invite Member</button>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {members.map(m => (
          <div key={m.id} className={`flex items-center justify-between px-4 py-3 ${!m.active ? "opacity-40" : ""}`}>
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gray-200 text-sm dark:bg-gray-700">{m.name[0]}</div>
              <div><p className="text-sm font-medium">{m.name}</p><p className="text-xs text-gray-400">{m.email}</p></div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs">{m.roleIcon} {m.role}</span>
              {m.role !== "owner" && <button onClick={() => onRemove(m.id)} className="text-xs text-red-600">Remove</button>}
            </div>
          </div>
        ))}
      </div>
      {pendingInvites.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-2">Pending Invites ({pendingInvites.length})</h3>
          {pendingInvites.map(i => (
            <div key={i.email} className="flex items-center justify-between rounded border px-3 py-2 text-sm dark:border-gray-700">
              <span>{i.email} — <span className="capitalize text-gray-400">{i.role}</span></span>
              <button onClick={() => onRevokeInvite(i.email)} className="text-xs text-red-600">Revoke</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
