"use client";

interface InviteInfo { invite_id: string; email: string; role: string; accepted: boolean; }
interface APIDeveloperInviteCardProps { invites: InviteInfo[]; appName: string; }

export default function APIDeveloperInviteCard({ invites, appName }: APIDeveloperInviteCardProps) {
  const pending = invites.filter((i) => !i.accepted).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✉️ Developer Invites</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{pending} pending / {invites.length} total</span>
      </div>
      {invites.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No invites</p>
      ) : (
        <div className="space-y-1">
          {invites.map((i) => (
            <div key={i.invite_id} className={`flex items-center justify-between text-[11px] ${i.accepted ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${i.accepted ? "bg-green-500" : "bg-yellow-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{i.email}</span>
              </div>
              <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{i.role}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
