"use client";

interface InstallFlowPageProps { appName: string; orgName: string; flowType: string; permissionCount: number; hasConfig: boolean; }

export function InstallFlowPage({ appName, orgName, flowType, permissionCount, hasConfig }: InstallFlowPageProps) {
  return (
    <div className="mx-auto max-w-lg p-6">
      <h2 className="text-xl font-bold">Install {appName}</h2>
      <p className="mt-1 text-sm text-gray-500">to {orgName}</p>
      <div className="mt-4 space-y-2 text-sm">
        <p>📋 {permissionCount} permission{permissionCount !== 1 ? "s" : ""} requested</p>
        {hasConfig && <p>⚙️ Configuration required</p>}
        <p className="capitalize">📦 {flowType} install flow</p>
      </div>
    </div>
  );
}
