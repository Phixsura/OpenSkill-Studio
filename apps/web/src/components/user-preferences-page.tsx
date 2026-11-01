"use client";
import { useState } from "react";

interface Prefs { theme: string; language: string; notificationsEnabled: boolean; emailDigest: string; defaultView: string; showBeta: boolean; autoUpdate: boolean; }

export function UserPreferencesPage({ prefs, onSave }: { prefs: Prefs; onSave?: (prefs: Prefs) => void }) {
  const [local, setLocal] = useState(prefs);
  const set = <K extends keyof Prefs>(k: K, v: Prefs[K]) => setLocal({ ...local, [k]: v });

  return (
    <div className="space-y-4 max-w-lg">
      <h3 className="font-bold text-sm">Preferences</h3>
      <div className="space-y-3">
        <div>
          <label className="text-xs font-medium block mb-1">Theme</label>
          <div className="flex gap-1">
            {["system", "light", "dark"].map(t => (
              <button key={t} onClick={() => set("theme", t)}
                className={`text-xs px-3 py-1 rounded-full capitalize ${local.theme === t ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{t}</button>
            ))}
          </div>
        </div>
        <div>
          <label className="text-xs font-medium block mb-1">Default View</label>
          <div className="flex gap-1">
            {["grid", "list"].map(v => (
              <button key={v} onClick={() => set("defaultView", v)}
                className={`text-xs px-3 py-1 rounded-full capitalize ${local.defaultView === v ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{v}</button>
            ))}
          </div>
        </div>
        <div>
          <label className="text-xs font-medium block mb-1">Email Digest</label>
          <div className="flex gap-1">
            {["none", "daily", "weekly"].map(d => (
              <button key={d} onClick={() => set("emailDigest", d)}
                className={`text-xs px-3 py-1 rounded-full capitalize ${local.emailDigest === d ? "bg-blue-500 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{d}</button>
            ))}
          </div>
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={local.showBeta} onChange={e => set("showBeta", e.target.checked)} />
          Show beta extensions
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={local.autoUpdate} onChange={e => set("autoUpdate", e.target.checked)} />
          Auto-update extensions
        </label>
      </div>
      <button onClick={() => onSave?.(local)} className="w-full bg-blue-500 text-white py-2 rounded-lg text-sm">Save Preferences</button>
    </div>
  );
}
