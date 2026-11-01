"use client";

import { useState } from "react";

interface SsoProvider { id: string; label: string; fields: string[]; }
interface SsoConfigFormProps { providers: SsoProvider[]; onSave: (provider: string, config: Record<string, string>) => void; }

export function SsoConfigForm({ providers, onSave }: SsoConfigFormProps) {
  const [selected, setSelected] = useState(providers[0]?.id ?? "");
  const [values, setValues] = useState<Record<string, string>>({});
  const provider = providers.find(p => p.id === selected);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">SSO Configuration</h2>
      <div className="flex gap-2">
        {providers.map(p => (
          <button key={p.id} onClick={() => { setSelected(p.id); setValues({}); }}
            className={`rounded px-3 py-1.5 text-sm ${selected === p.id ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
            {p.label}
          </button>
        ))}
      </div>
      {provider && (
        <div className="space-y-3">
          {provider.fields.map(field => (
            <div key={field}>
              <label className="text-sm text-gray-500">{field.replace(/_/g, " ")}</label>
              <input value={values[field] ?? ""} onChange={e => setValues({ ...values, [field]: e.target.value })}
                type={field.includes("secret") || field.includes("certificate") ? "password" : "text"}
                className="mt-0.5 w-full rounded border px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
            </div>
          ))}
          <button onClick={() => onSave(selected, values)}
            className="w-full rounded bg-blue-600 py-2 text-sm font-medium text-white">
            Save Configuration
          </button>
        </div>
      )}
    </div>
  );
}
