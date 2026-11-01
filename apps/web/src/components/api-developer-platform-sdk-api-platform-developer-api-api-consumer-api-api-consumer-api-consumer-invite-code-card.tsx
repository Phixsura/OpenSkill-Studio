"use client";

interface Invite { code: string; usedCount: number; maxUses: number; disabled: boolean; expiresAt: string; planId: string | null; }
interface Props { invites: Invite[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerInviteCodeCard({ invites, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎟️ Invite Codes</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {invites.length} codes</p>
      </div>
      {invites.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No invite codes</p>
      ) : (
        <div className="space-y-2">
          {invites.map((inv) => (
            <div key={inv.code} className={`rounded-lg p-2 ${inv.disabled ? "bg-gray-100 opacity-60 dark:bg-gray-800" : "bg-gray-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <code className="font-mono font-bold text-gray-700 dark:text-gray-300">{inv.code}</code>
                <div className="flex gap-1">
                  {inv.disabled && <span className="rounded bg-red-100 px-1 py-0.5 text-[9px] text-red-600 dark:bg-red-900/30 dark:text-red-400">disabled</span>}
                  {inv.planId && <span className="rounded bg-blue-100 px-1 py-0.5 text-[9px] text-blue-600 dark:bg-blue-900/30 dark:text-blue-400">{inv.planId}</span>}
                </div>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">{inv.usedCount}/{inv.maxUses} used · Expires {inv.expiresAt}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
