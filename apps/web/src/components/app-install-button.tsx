"use client";

interface AppInstallButtonProps { appName: string; installed: boolean;
  activeInstalls: number; onInstall: () => void; onUninstall: () => void; }

export function AppInstallButton({ appName, installed, activeInstalls, onInstall, onUninstall }: AppInstallButtonProps) {
  return (
    <div className="flex items-center gap-3">
      <button onClick={installed ? onUninstall : onInstall}
        className={`px-4 py-2 text-sm rounded-lg font-medium transition ${
          installed ? "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-red-100 hover:text-red-600"
                   : "bg-blue-600 text-white hover:bg-blue-700"
        }`}>
        {installed ? "Uninstall" : "Install"}
      </button>
      <span className="text-xs text-gray-400">{activeInstalls.toLocaleString()} installs</span>
    </div>
  );
}
