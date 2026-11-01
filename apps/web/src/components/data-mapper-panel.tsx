"use client";

import { useState } from "react";

interface FieldMapping {
  sourceField: string;
  targetField: string;
  transform: string;
}

interface DataMapping {
  id: string;
  name: string;
  sourceConnector: string;
  targetConnector: string;
  fieldMappings: FieldMapping[];
}

const transformColors: Record<string, string> = {
  rename: "bg-gray-100 text-gray-600 dark:bg-gray-800",
  cast: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  default: "bg-green-100 text-green-700 dark:bg-green-900/30",
  template: "bg-purple-100 text-purple-700 dark:bg-purple-900/30",
  extract: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  uppercase: "bg-orange-100 text-orange-700 dark:bg-orange-900/30",
  lowercase: "bg-orange-100 text-orange-700 dark:bg-orange-900/30",
};

export function DataMapperPanel({
  mappings,
  onTest,
  onDelete,
}: {
  mappings: DataMapping[];
  onTest?: (id: string) => void;
  onDelete?: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔄 Data Mappings</h2>

      <div className="space-y-2">
        {mappings.map((m) => (
          <div key={m.id} className="rounded-xl border dark:border-gray-700 overflow-hidden">
            <div className="flex items-center justify-between p-3 cursor-pointer"
              onClick={() => setExpanded(expanded === m.id ? null : m.id)}>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{m.name}</span>
                <span className="text-xs text-gray-400">
                  {m.sourceConnector} → {m.targetConnector}
                </span>
                <span className="text-xs text-gray-400">{m.fieldMappings.length} fields</span>
              </div>
              <div className="flex gap-1">
                <button onClick={(e) => { e.stopPropagation(); onTest?.(m.id); }}
                  className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Test</button>
                <button onClick={(e) => { e.stopPropagation(); onDelete?.(m.id); }}
                  className="text-xs text-red-500">✕</button>
              </div>
            </div>

            {expanded === m.id && (
              <div className="border-t dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-gray-500">
                      <th className="text-left pb-1">Source</th>
                      <th className="text-center pb-1">Transform</th>
                      <th className="text-left pb-1">Target</th>
                    </tr>
                  </thead>
                  <tbody>
                    {m.fieldMappings.map((fm, i) => (
                      <tr key={i}>
                        <td className="py-0.5"><code>{fm.sourceField}</code></td>
                        <td className="text-center py-0.5">
                          <span className={`px-1.5 py-0.5 rounded ${transformColors[fm.transform] || "bg-gray-100"}`}>
                            {fm.transform}
                          </span>
                        </td>
                        <td className="py-0.5"><code>{fm.targetField}</code></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
