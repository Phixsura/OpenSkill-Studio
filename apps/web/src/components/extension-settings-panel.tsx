"use client";

import { useState } from "react";

interface SettingField {
  key: string;
  label: string;
  type: "text" | "number" | "toggle" | "select";
  value: string;
  description: string;
  options?: string[];
  required?: boolean;
}

interface SettingsGroup {
  name: string;
  icon: string;
  fields: SettingField[];
}

export function ExtensionSettingsPanel({
  groups,
  extensionName,
  onSave,
  onReset,
}: {
  groups: SettingsGroup[];
  extensionName: string;
  onSave?: (values: Record<string, string>) => void;
  onReset?: () => void;
}) {
  const initialValues: Record<string, string> = {};
  groups.forEach((g) => g.fields.forEach((f) => { initialValues[f.key] = f.value; }));
  const [values, setValues] = useState(initialValues);
  const [saved, setSaved] = useState(false);
  const [activeGroup, setActiveGroup] = useState(groups[0]?.name || "");

  const update = (key: string, val: string) => {
    setValues((prev) => ({ ...prev, [key]: val }));
    setSaved(false);
  };

  const handleSave = () => {
    onSave?.(values);
    setSaved(true);
  };

  const currentGroup = groups.find((g) => g.name === activeGroup);

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 border-b dark:border-gray-700">
        <h2 className="font-bold">⚙️ {extensionName} Settings</h2>
      </div>

      <div className="flex divide-x dark:divide-gray-700">
        {/* Group tabs */}
        <div className="w-48 bg-gray-50/50 dark:bg-gray-800/50 p-2">
          {groups.map((g) => (
            <button key={g.name} onClick={() => setActiveGroup(g.name)}
              className={`w-full text-left px-3 py-2 rounded text-sm ${
                activeGroup === g.name ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300" : "text-gray-600 dark:text-gray-300"
              }`}>
              {g.icon} {g.name}
            </button>
          ))}
        </div>

        {/* Fields */}
        <div className="flex-1 p-4 space-y-4">
          {currentGroup?.fields.map((field) => (
            <div key={field.key}>
              <label className="block text-sm font-medium mb-1">
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              <p className="text-xs text-gray-400 mb-1">{field.description}</p>
              {field.type === "toggle" ? (
                <button onClick={() => update(field.key, values[field.key] === "true" ? "false" : "true")}
                  className={`w-10 h-5 rounded-full transition ${values[field.key] === "true" ? "bg-blue-500" : "bg-gray-300 dark:bg-gray-600"}`}>
                  <div className={`w-4 h-4 rounded-full bg-white transition ${values[field.key] === "true" ? "translate-x-5" : "translate-x-0.5"}`} />
                </button>
              ) : field.type === "select" ? (
                <select value={values[field.key]} onChange={(e) => update(field.key, e.target.value)}
                  className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm">
                  {field.options?.map((o) => <option key={o} value={o}>{o}</option>)}
                </select>
              ) : (
                <input type={field.type} value={values[field.key]}
                  onChange={(e) => update(field.key, e.target.value)}
                  className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm" />
              )}
            </div>
          ))}

          <div className="flex items-center gap-3 pt-2">
            <button onClick={handleSave} className="rounded-lg bg-blue-600 text-white px-4 py-2 text-sm font-medium">
              Save Settings
            </button>
            {onReset && (
              <button onClick={onReset} className="text-sm text-gray-500 hover:text-gray-700">Reset to defaults</button>
            )}
            {saved && <span className="text-sm text-green-500">✅ Saved!</span>}
          </div>
        </div>
      </div>
    </div>
  );
}
