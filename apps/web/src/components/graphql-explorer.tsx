"use client";

import { useState } from "react";

interface GqlField { name: string; type: string; description: string; deprecated: boolean; }
interface GqlType { name: string; kind: string; fields: GqlField[]; fieldCount: number; description: string; }
interface GraphqlExplorerProps { types: GqlType[]; queryCount: number; mutationCount: number; }

export function GraphqlExplorer({ types, queryCount, mutationCount }: GraphqlExplorerProps) {
  const [selected, setSelected] = useState<string | null>(null);
  const selectedType = types.find(t => t.name === selected);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">GraphQL Schema</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{types.length} types</span>
          <span>{queryCount} queries</span>
          <span>{mutationCount} mutations</span>
        </div>
      </div>
      <div className="flex flex-wrap gap-1">
        {types.map(t => (
          <button key={t.name} onClick={() => setSelected(t.name)}
            className={`rounded px-2 py-1 text-xs font-mono ${selected === t.name ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
            {t.name}
          </button>
        ))}
      </div>
      {selectedType && (
        <div className="rounded-lg border p-3 dark:border-gray-700">
          <p className="text-sm font-bold font-mono">{selectedType.name}</p>
          {selectedType.description && <p className="text-xs text-gray-400 mt-1">{selectedType.description}</p>}
          <div className="mt-2 space-y-1">
            {selectedType.fields.map(f => (
              <div key={f.name} className={`text-xs ${f.deprecated ? "line-through opacity-50" : ""}`}>
                <span className="font-mono font-medium">{f.name}</span>
                <span className="text-gray-400">: {f.type}</span>
                {f.description && <span className="ml-2 text-gray-500">— {f.description}</span>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
