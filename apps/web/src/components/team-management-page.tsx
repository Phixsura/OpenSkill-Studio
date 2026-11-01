"use client";

interface Member { id: string; name: string; email: string; role: string;
  roleLabel: string; roleIcon: string; active: boolean; }
interface TeamManagementPageProps { members: Member[]; pendingInvites: number;
  seatsRemaining: number; canInvite: boolean;
  onInvite: () => void; onRemove: (id: string) => void; onChangeRole: (id: string, role: string) => void; }

export function TeamManagementPage({ members, pendingInvites, seatsRemaining, canInvite,
  onInvite, onRemove, onChangeRole }: TeamManagementPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">👥 Team</h2>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">{members.length} members · {seatsRemaining} seats left</span>
          {pendingInvites > 0 && <span className="text-xs text-yellow-600">{pendingInvites} pending</span>}
          {canInvite && <button onClick={onInvite} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white">+ Invite</button>}
        </div>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {members.map(m => (
          <div key={m.id} className={`flex items-center justify-between px-4 py-3 ${!m.active ? "opacity-40" : ""}`}>
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gray-200 text-sm dark:bg-gray-700">
                {m.name[0]?.toUpperCase() ?? "?"}
              </div>
              <div>
                <p className="text-sm font-medium">{m.name}</p>
                <p className="text-xs text-gray-400">{m.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs">{m.roleIcon} {m.roleLabel}</span>
              {m.role !== "owner" && (
                <button onClick={() => onRemove(m.id)} className="text-xs text-red-600 hover:underline">Remove</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
