"use client";

interface DeployNotif { deploymentId: string; version: string; environment: string;
  deployer: string; deployStatus: string; channelsNotified: number; }
interface DeployNotifLogProps { notifications: DeployNotif[]; total: number; }

const STATUS_ICONS: Record<string, string> = { success: "✅", failed: "❌", rollback: "⏪" };

export function DeployNotifLog({ notifications, total }: DeployNotifLogProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📣 Deploy Notifications</h3>
        <span className="text-xs text-gray-400">{total} notifications</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {notifications.map(n => (
          <div key={n.deploymentId} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span>{STATUS_ICONS[n.deployStatus] ?? "⚪"}</span>
              <span className="font-mono">v{n.version}</span>
              <span className="text-gray-400">{n.environment}</span>
            </div>
            <span className="text-gray-400">{n.deployer} · {n.channelsNotified} channels</span>
          </div>
        ))}
      </div>
    </div>
  );
}
