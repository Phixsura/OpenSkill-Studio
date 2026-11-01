"use client";

interface InviteInfo { invite_id: string; email: string; role: string; status: string; hours_remaining: number; }
interface Props { invites: InviteInfo[]; pendingCount: number; appName: string; }

const statusStyle: Record<string, string> = { pending: "text-yellow-600 dark:text-yellow-400", accepted: "text-green-600 dark:text-green-400", expired: "text-gray-400", revoked: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerInvitationCard({ invites, pendingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✉️ Invitations</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {pendingCount > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">{pendingCount} pending</span>}
      </div>
      {invites.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No invitations</p>
      ) : (
        <div className="space-y-1">
          {invites.map((i) => (
            <div key={i.invite_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{i.email}</span>
              <span className={statusStyle[i.status] ?? "text-gray-400"}>{i.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
