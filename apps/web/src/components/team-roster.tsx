"use client";

interface Member { id: string; name: string; email: string; role: string; active: boolean; joinedAt: string; }
interface TeamRosterProps { members: Member[]; onChangeRole: (id: string, role: string) => void; onRemove: (id: string) => void; }

const roleBadge: Record<string, string> = {
  owner: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  admin: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  editor: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  viewer: "bg-gray-100 text-gray-600 dark:bg-gray-800",
};

export function TeamRoster({ members, onChangeRole, onRemove }: TeamRosterProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Team ({members.length})</h3>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {members.map(m => (
          <div key={m.id} className={`flex items-center justify-between px-4 py-3 ${!m.active ? "opacity-40" : ""}`}>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{m.name}</span>
                <span className={`rounded px-1.5 py-0.5 text-xs ${roleBadge[m.role] ?? ""}`}>{m.role}</span>
              </div>
              <p className="text-xs text-gray-400">{m.email}</p>
            </div>
            {m.role !== "owner" && m.active && (
              <button onClick={() => onRemove(m.id)} className="text-xs text-red-600 hover:underline">Remove</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
