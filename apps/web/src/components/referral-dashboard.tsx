"use client";

interface ReferralDashboardProps { code: string; signups: number; totalRewards: string; onCopyCode: () => void; }

export function ReferralDashboard({ code, signups, totalRewards, onCopyCode }: ReferralDashboardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Referral Program</h3>
      <div className="mt-3 flex items-center gap-2 rounded bg-gray-50 p-3 dark:bg-gray-800">
        <code className="flex-1 text-sm font-bold">{code}</code>
        <button onClick={onCopyCode} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">Copy</button>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-4 text-center">
        <div><p className="text-2xl font-bold">{signups}</p><p className="text-xs text-gray-400">Signups</p></div>
        <div><p className="text-2xl font-bold">{totalRewards}</p><p className="text-xs text-gray-400">Earned</p></div>
      </div>
      <p className="mt-3 text-xs text-gray-400">Earn $5 for each developer who signs up with your code!</p>
    </div>
  );
}
