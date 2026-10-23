"use client";

interface Member { user_id: string; display_name: string; role: string; joined: string; }
interface AccessControlMemberListProps { members: Member[]; currentUserRole: string;
  onChangeRole: (userId: string, newRole: string) => void; onRemove: (userId: string) => void; }

const roleBadge: Record<string, string> = {
  owner: "bg-purple-100 text-purple-700 dark:bg-purple-900/30", admin: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  developer: "bg-green-100 text-green-700 dark:bg-green-900/30", viewer: "bg-gray-100 text-gray-600 dark:bg-gray-800",
};

export function AccessControlMemberList({ members, currentUserRole, onChangeRole, onRemove }: AccessControlMemberListProps) {
  const canManage = currentUserRole === "owner" || currentUserRole === "admin";
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Team Members</h2>
      <div className="space-y-2">
        {members.map(m => (
          <div key={m.user_id} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
            <div>
              <p className="font-medium">{m.display_name}</p>
              <p className="text-xs text-gray-400">Joined {new Date(m.joined).toLocaleDateString()}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${roleBadge[m.role] ?? ""}`}>{m.role}</span>
              {canManage && m.role !== "owner" && (
                <button onClick={() => onRemove(m.user_id)} className="text-xs text-red-500 hover:underline">Remove</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
