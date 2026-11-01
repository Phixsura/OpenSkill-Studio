"use client";
import { useState } from "react";

interface TenantConfig { theme: string; locale: string; timezone: string;
  branding: { accentColor: string; appName: string; }; }
interface TenantSettingsFormProps { orgId: string; config: TenantConfig;
  onSave: (patch: Partial<TenantConfig>) => void; }

export function TenantSettingsForm({ orgId, config, onSave }: TenantSettingsFormProps) {
  const [theme, setTheme] = useState(config.theme);
  const [appName, setAppName] = useState(config.branding.appName);
  const [accent, setAccent] = useState(config.branding.accentColor);

  return (
    <div className="rounded-xl border p-5 dark:border-gray-700 max-w-lg">
      <h3 className="font-semibold mb-1">⚙️ Organization Settings</h3>
      <p className="text-xs text-gray-400 mb-4">{orgId}</p>
      <div className="space-y-4">
        <div>
          <label className="block text-xs font-medium mb-1">Theme</label>
          <select value={theme} onChange={e => setTheme(e.target.value)}
            className="w-full px-3 py-1.5 border rounded text-sm dark:bg-gray-800 dark:border-gray-600">
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium mb-1">App Name</label>
          <input value={appName} onChange={e => setAppName(e.target.value)}
            className="w-full px-3 py-1.5 border rounded text-sm dark:bg-gray-800 dark:border-gray-600" />
        </div>
        <div>
          <label className="block text-xs font-medium mb-1">Accent Color</label>
          <div className="flex gap-2">
            <input type="color" value={accent} onChange={e => setAccent(e.target.value)} className="w-10 h-9 rounded cursor-pointer" />
            <input value={accent} onChange={e => setAccent(e.target.value)}
              className="flex-1 px-3 py-1.5 border rounded text-sm font-mono dark:bg-gray-800 dark:border-gray-600" />
          </div>
        </div>
        <button onClick={() => onSave({ theme, branding: { accentColor: accent, appName } })}
          className="w-full py-2 bg-blue-600 text-white text-sm rounded font-medium hover:bg-blue-700">Save Settings</button>
      </div>
    </div>
  );
}
