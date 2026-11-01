"use client";

interface MemberInfo {
  user_id: string;
  email: string;
  display_name: string;
  role: "owner" | "admin" | "member" | "viewer";
}

interface TeamMemberCardProps {
  members: MemberInfo[];
  appName: string;
}

const ROLE_STYLES: Record<string, { bg: string; text: string }> = {
  owner: {
    bg: "bg-purple-100 dark:bg-purple-900/30",
    text: "text-purple-700 dark:text-purple-400",
  },
  admin: { bg: "bg-red-100 dark:bg-red-900/30", text: "text-red-700 dark:text-red-400" },
  member: { bg: "bg-blue-100 dark:bg-blue-900/30", text: "text-blue-700 dark:text-blue-400" },
  viewer: { bg: "bg-gray-100 dark:bg-gray-800", text: "text-gray-600 dark:text-gray-400" },
};

export default function TeamMemberCard({ members, appName }: TeamMemberCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Team Members</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{members.length} members</span>
      </div>

      {members.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No team members</p>
      ) : (
        <div className="space-y-1.5">
          {members.map((m) => {
            const rs = ROLE_STYLES[m.role] ?? ROLE_STYLES.viewer;
            return (
              <div
                key={m.user_id}
                className="flex items-center justify-between rounded px-2.5 py-2 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <div>
                  <span className="text-sm text-gray-800 dark:text-gray-200">{m.display_name}</span>
                  <p className="text-[11px] text-gray-400">{m.email}</p>
                </div>
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${rs.bg} ${rs.text}`}
                >
                  {m.role}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
