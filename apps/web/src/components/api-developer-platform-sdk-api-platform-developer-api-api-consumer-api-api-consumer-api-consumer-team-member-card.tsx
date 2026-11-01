"use client";

interface Member { id: string; email: string; role: string; joinedAt: string; }
interface Props { members: Member[]; consumerId: string; appName: string; }

const roleBg: Record<string, string> = {
  owner: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  admin: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  member: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  viewer: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerTeamMemberCard({ members, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👥 Team Members</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {members.length} members</p>
      </div>
      {members.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No team members</p>
      ) : (
        <div className="space-y-1">
          {members.map((m) => (
            <div key={m.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <span className="text-gray-700 dark:text-gray-300">{m.email}</span>
              <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${roleBg[m.role] ?? ""}`}>{m.role}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
