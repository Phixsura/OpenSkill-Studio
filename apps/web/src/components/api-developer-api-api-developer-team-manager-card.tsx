"use client";

interface MemberInfo { developer_id: string; role: string; }
interface TeamInfo { team_id: string; name: string; members: MemberInfo[]; member_count: number; }
interface Props { teams: TeamInfo[]; appName: string; }

const rBadge: Record<string, string> = { owner: "bg-purple-100 text-purple-700", admin: "bg-blue-100 text-blue-700", developer: "bg-green-100 text-green-700", viewer: "bg-gray-100 text-gray-600" };

export default function APIDeveloperAPIApiDeveloperTeamManagerCard({ teams, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👥 Developer Teams</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {teams.length} teams</p>
      </div>
      {teams.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No teams</p>
      ) : (
        <div className="space-y-3">
          {teams.map((t) => (
            <div key={t.team_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{t.name}</span>
                <span className="text-gray-400">{t.member_count} members</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {t.members.slice(0, 5).map((m) => (
                  <span key={m.developer_id} className={`rounded px-1 py-0.5 text-[9px] ${rBadge[m.role] ?? ""}`}>{m.developer_id}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
