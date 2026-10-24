"use client";

interface TeamStats { total: number; pending_invites: number; plan_limit: number; seats_remaining: number; }
interface TeamPageLayoutProps { stats: TeamStats; canInvite: boolean; onInvite: () => void; children: React.ReactNode; }

export function TeamPageLayout({ stats, canInvite, onInvite, children }: TeamPageLayoutProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">Team</h1>
          <p className="text-sm text-gray-400">{stats.total} members · {stats.seats_remaining} seats remaining</p>
        </div>
        <button onClick={onInvite} disabled={!canInvite}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50">
          {canInvite ? "+ Invite Member" : "Team Full"}
        </button>
      </div>
      {stats.pending_invites > 0 && (
        <div className="rounded bg-yellow-50 px-3 py-2 text-sm text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300">
          ⏳ {stats.pending_invites} pending invite{stats.pending_invites > 1 ? "s" : ""}
        </div>
      )}
      <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
        {children}
      </div>
    </div>
  );
}
