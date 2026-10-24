"use client";

interface Member { userId: string; role: string; addedBy: string; }
interface TeamRolesTableProps { members: Member[]; roles: string[];
  onChangeRole: (userId: string, newRole: string) => void; onRemove: (userId: string) => void; }

const ROLE_COLORS: Record<string, string> = {
  owner: "bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400",
  admin: "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400",
  developer: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400",
  viewer: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400",
};

export function TeamRolesTable({ members, roles, onChangeRole, onRemove }: TeamRolesTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">👥 Team Members</h3>
        <span className="text-xs text-gray-400">{members.length} members</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {members.map(m => (
          <div key={m.userId} className="flex items-center justify-between px-4 py-3">
            <div>
              <span className="text-sm font-medium">{m.userId}</span>
              <span className="text-xs text-gray-400 ml-2">invited by {m.addedBy}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={`px-2 py-0.5 text-[10px] rounded-full ${ROLE_COLORS[m.role] ?? ""}`}>{m.role}</span>
              {m.role !== "owner" && (
                <button onClick={() => onRemove(m.userId)} className="text-xs text-red-500 hover:underline">Remove</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
