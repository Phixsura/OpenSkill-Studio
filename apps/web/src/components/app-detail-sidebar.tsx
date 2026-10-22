"use client";

interface AppDetailSidebarProps {
  healthScore: number; healthStatus: string; installCount: number;
  permissionCount: number; hasSandbox: boolean; hasUi: boolean; errorRate: number;
}

export function AppDetailSidebar({ healthScore, healthStatus, installCount, permissionCount, hasSandbox, hasUi, errorRate }: AppDetailSidebarProps) {
  const healthColor = healthScore >= 95 ? "green" : healthScore >= 80 ? "yellow" : "red";
  return (
    <div className="space-y-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="text-center">
        <p className={`text-3xl font-bold text-${healthColor}-600`}>{healthScore}</p>
        <p className="text-xs capitalize text-gray-500">{healthStatus}</p>
      </div>
      <hr className="dark:border-gray-700" />
      <div className="space-y-2 text-sm">
        <div className="flex justify-between"><span className="text-gray-500">Installs</span><span className="font-medium">{installCount}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Permissions</span><span className="font-medium">{permissionCount}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Error Rate</span><span className="font-medium">{errorRate}%</span></div>
        <div className="flex justify-between"><span className="text-gray-500">Sandbox</span><span>{hasSandbox ? "✅" : "—"}</span></div>
        <div className="flex justify-between"><span className="text-gray-500">UI Extension</span><span>{hasUi ? "✅" : "—"}</span></div>
      </div>
    </div>
  );
}
