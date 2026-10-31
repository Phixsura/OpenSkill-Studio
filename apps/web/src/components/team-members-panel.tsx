"use client";

interface Member { userId: string; displayName: string; role: string; joinedAt: number; }

const roleColors: Record<string, string> = {
  owner: "bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400",
  admin: "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400",
  developer: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400",
  viewer: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400",
};

export function TeamMembersPanel({ members, onRemove, onInvite }: {
  members: Member[]; onRemove?: (userId: string) => void; onInvite?: () => void;
}) {
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <h3 className="font-bold text-sm">Team Members ({members.length})</h3>
        <button onClick={onInvite} className="text-xs bg-blue-500 text-white px-3 py-1 rounded-lg">+ Invite</button>
      </div>
      <div className="space-y-1">
        {members.map(m => (
          <div key={m.userId} className="flex items-center justify-between border dark:border-gray-700 rounded-lg p-2.5">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-xs font-bold">
                {m.displayName.charAt(0).toUpperCase()}
              </div>
              <div>
                <span className="text-sm font-medium block">{m.displayName}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded capitalize ${roleColors[m.role] || ""}`}>{m.role}</span>
              </div>
            </div>
            {m.role !== "owner" && <button onClick={() => onRemove?.(m.userId)} className="text-xs text-red-400 hover:text-red-600">Remove</button>}
          </div>
        ))}
      </div>
    </div>
  );
}
