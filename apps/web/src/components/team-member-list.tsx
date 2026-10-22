"use client";

interface TeamMember { userId: string; displayName: string; role: string; email?: string; }

interface TeamMemberListProps { members: TeamMember[]; onRemove?: (userId: string) => void; onChangeRole?: (userId: string, role: string) => void; }

const ROLE_BADGES: Record<string, string> = { owner: "bg-purple-100 text-purple-800", admin: "bg-blue-100 text-blue-800", member: "bg-gray-100 text-gray-800", viewer: "bg-gray-100 text-gray-500" };

export function TeamMemberList({ members, onRemove, onChangeRole }: TeamMemberListProps) {
  if (members.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No team members</p>;
  return (
    <div className="space-y-2">
      {members.map(m => (
        <div key={m.userId} className="flex items-center gap-3 rounded border border-gray-200 p-3 dark:border-gray-700">
          <div className="flex-1">
            <span className="font-medium">{m.displayName}</span>
            {m.email && <span className="ml-2 text-xs text-gray-500">{m.email}</span>}
          </div>
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${ROLE_BADGES[m.role] ?? ROLE_BADGES.member}`}>{m.role}</span>
          {onRemove && m.role !== "owner" && <button onClick={() => onRemove(m.userId)} className="text-xs text-red-500">Remove</button>}
        </div>
      ))}
    </div>
  );
}
