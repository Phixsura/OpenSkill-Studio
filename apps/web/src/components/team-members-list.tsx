"use client";

interface Member { id: string; email: string; role: string; status: string; }
interface TeamMembersListProps { members: Member[]; onRemove: (id: string) => void; onChangeRole: (id: string, role: string) => void; }

const ROLE_COLORS: Record<string, string> = {
  owner: "bg-purple-100 text-purple-700", admin: "bg-blue-100 text-blue-700",
  developer: "bg-green-100 text-green-700", viewer: "bg-gray-100 text-gray-600",
};

export function TeamMembersList({ members, onRemove, onChangeRole }: TeamMembersListProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Team Members ({members.length})</h3>
      <ul className="mt-3 space-y-2">
        {members.map(m => (
          <li key={m.id} className="flex items-center justify-between rounded border p-2 dark:border-gray-700">
            <div>
              <p className="text-sm font-medium">{m.email}</p>
              <span className={`rounded-full px-2 py-0.5 text-xs ${ROLE_COLORS[m.role] || ""}`}>{m.role}</span>
              {m.status === "pending" && <span className="ml-1 text-xs text-yellow-600">⏳ pending</span>}
            </div>
            {m.role !== "owner" && (
              <button onClick={() => onRemove(m.id)} className="text-xs text-red-500">Remove</button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
