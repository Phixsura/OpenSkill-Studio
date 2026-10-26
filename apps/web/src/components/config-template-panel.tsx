"use client";

import { useState } from "react";

interface TemplateVar { name: string; varType: string; required: boolean; default: string; enumValues?: string[]; }
interface Template { id: string; name: string; variables: TemplateVar[]; }

export function ConfigTemplatePanel({
  template,
  renderedConfig,
  onRender,
}: {
  template: Template;
  renderedConfig: Record<string, string> | null;
  onRender?: (values: Record<string, string>) => void;
}) {
  const [values, setValues] = useState<Record<string, string>>({});

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📝 {template.name}</h2>
      <div className="space-y-2">
        {template.variables.map((v) => (
          <div key={v.name}>
            <label className="text-xs text-gray-500 block">{v.name} {v.required && <span className="text-red-500">*</span>}</label>
            {v.enumValues ? (
              <select value={values[v.name] || v.default} onChange={(e) => setValues({ ...values, [v.name]: e.target.value })}
                className="w-full rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm">
                {v.enumValues.map((ev) => <option key={ev} value={ev}>{ev}</option>)}
              </select>
            ) : (
              <input type="text" value={values[v.name] || v.default}
                onChange={(e) => setValues({ ...values, [v.name]: e.target.value })}
                placeholder={v.default || v.name}
                className="w-full rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm font-mono" />
            )}
          </div>
        ))}
      </div>
      <button onClick={() => onRender?.(values)} className="text-sm bg-green-600 text-white px-4 py-1.5 rounded-lg">Render Config</button>
      {renderedConfig && (
        <pre className="rounded-lg border dark:border-gray-700 bg-gray-950 p-3 text-xs text-green-400 font-mono">
          {JSON.stringify(renderedConfig, null, 2)}
        </pre>
      )}
    </div>
  );
}
