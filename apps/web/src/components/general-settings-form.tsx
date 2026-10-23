"use client";

interface Field { key: string; label: string; type: string; value: string;
  required?: boolean; maxLength?: number; help?: string; options?: string[]; }
interface GeneralSettingsFormProps { fields: Field[]; currentVersion: string;
  errors: string[]; onSave: (data: Record<string, string>) => void; }

export function GeneralSettingsForm({ fields, currentVersion, errors, onSave }: GeneralSettingsFormProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⚙️ General Settings</h2>
        <span className="text-xs text-gray-400">v{currentVersion}</span>
      </div>
      {errors.length > 0 && (
        <div className="rounded-lg bg-red-50 p-3 dark:bg-red-900/10">
          {errors.map((e, i) => <p key={i} className="text-xs text-red-600">⚠ {e}</p>)}
        </div>
      )}
      <div className="space-y-3">
        {fields.map(f => (
          <div key={f.key}>
            <label className="block text-xs text-gray-400 mb-1">
              {f.label}{f.required && <span className="text-red-500"> *</span>}
            </label>
            {f.type === "select" && f.options ? (
              <select defaultValue={f.value}
                className="w-full rounded border px-3 py-2 text-sm capitalize dark:bg-gray-800 dark:border-gray-600">
                {f.options.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            ) : f.type === "textarea" ? (
              <textarea defaultValue={f.value} rows={3} maxLength={f.maxLength}
                className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
            ) : (
              <input type={f.type === "url" ? "url" : f.type === "email" ? "email" : "text"}
                defaultValue={f.value} maxLength={f.maxLength}
                className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
            )}
            {f.help && <p className="mt-0.5 text-xs text-gray-400">{f.help}</p>}
          </div>
        ))}
      </div>
      <button onClick={() => onSave({})} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Save Settings</button>
    </div>
  );
}
