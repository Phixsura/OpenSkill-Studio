"use client";

interface TeamMember { name: string; email: string; role: string; avatarInitials: string; }
interface TeamMemberListProps { members: TeamMember[]; canManage: boolean;
  onChangeRole: (email: string, role: string) => void; onRemove: (email: string) => void; }

const ROLE_COLOR: Record<string, string> = {
  owner: "bg-purple-100 text-purple-700", admin: "bg-blue-100 text-blue-700",
  developer: "bg-green-100 text-green-700", viewer: "bg-gray-100 text-gray-600",
};

export function TeamMemberList({ members, canManage, onChangeRole, onRemove }: TeamMemberListProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">👥 Team ({members.length})</h3>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {members.map(m => (
          <div key={m.email} className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-500 text-white text-xs font-bold flex items-center justify-center">{m.avatarInitials}</div>
              <div>
                <p className="text-sm font-medium">{m.name}</p>
                <p className="text-xs text-gray-400">{m.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-0.5 rounded capitalize ${ROLE_COLOR[m.role] || ""}`}>{m.role}</span>
              {canManage && m.role !== "owner" && (
                <button onClick={() => onRemove(m.email)} className="text-xs text-red-500 hover:text-red-700">Remove</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
