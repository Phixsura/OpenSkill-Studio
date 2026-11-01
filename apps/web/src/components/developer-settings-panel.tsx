"use client";

import { useState } from "react";

interface Settings {
  displayName: string; emailNotifications: boolean; webhookNotifications: boolean;
  defaultRuntime: string; theme: string; timezone: string; autoDeploy: boolean; twoFactorEnabled: boolean;
}

const runtimes = ["node18", "node20", "python3.11", "python3.12", "deno", "bun"];
const themes = ["light", "dark", "system"];

export function DeveloperSettingsPanel({
  settings, onSave, onReset,
}: {
  settings: Settings; onSave?: (settings: Partial<Settings>) => void; onReset?: () => void;
}) {
  const [s, setS] = useState(settings);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⚙️ Developer Settings</h2>
        <div className="flex gap-1">
          <button onClick={() => onSave?.(s)} className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">Save</button>
          <button onClick={onReset} className="text-sm bg-gray-100 dark:bg-gray-800 px-3 py-1.5 rounded-lg">Reset</button>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <label className="text-xs text-gray-500 block mb-1">Display Name</label>
          <input type="text" value={s.displayName} onChange={(e) => setS({ ...s, displayName: e.target.value })}
            className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm" />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-500 block mb-1">Default Runtime</label>
            <select value={s.defaultRuntime} onChange={(e) => setS({ ...s, defaultRuntime: e.target.value })}
              className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm">
              {runtimes.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Theme</label>
            <select value={s.theme} onChange={(e) => setS({ ...s, theme: e.target.value })}
              className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm">
              {themes.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
        </div>

        <div className="space-y-2">
          {[
            { key: "emailNotifications", label: "Email Notifications" },
            { key: "webhookNotifications", label: "Webhook Notifications" },
            { key: "autoDeploy", label: "Auto Deploy on Push" },
            { key: "twoFactorEnabled", label: "Two-Factor Auth" },
          ].map(({ key, label }) => (
            <label key={key} className="flex items-center justify-between text-sm">
              <span>{label}</span>
              <input type="checkbox" checked={s[key as keyof Settings] as boolean}
                onChange={(e) => setS({ ...s, [key]: e.target.checked })}
                className="rounded" />
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
