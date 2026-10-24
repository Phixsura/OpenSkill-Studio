"use client";

interface OrgAppSettingsProps {
  autoUpgrade: boolean; allowThirdParty: boolean; maxApps: number; requireApproval: boolean;
  onSave: (settings: Record<string, unknown>) => void;
}

export function OrgAppSettings({ autoUpgrade, allowThirdParty, maxApps, requireApproval, onSave }: OrgAppSettingsProps) {
  return (
    <div className="space-y-4 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="font-semibold">App Settings</h4>
      <label className="flex items-center justify-between text-sm">
        <span>Auto-upgrade apps</span>
        <span className={autoUpgrade ? "text-green-600" : "text-gray-400"}>{autoUpgrade ? "On" : "Off"}</span>
      </label>
      <label className="flex items-center justify-between text-sm">
        <span>Allow third-party apps</span>
        <span className={allowThirdParty ? "text-green-600" : "text-gray-400"}>{allowThirdParty ? "On" : "Off"}</span>
      </label>
      <label className="flex items-center justify-between text-sm">
        <span>Max apps</span><span>{maxApps}</span>
      </label>
      <label className="flex items-center justify-between text-sm">
        <span>Require admin approval</span>
        <span className={requireApproval ? "text-yellow-600" : "text-gray-400"}>{requireApproval ? "Yes" : "No"}</span>
      </label>
    </div>
  );
}
