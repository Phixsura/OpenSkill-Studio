"use client";
import { useState } from "react";

interface GqlType { name: string; kind: string; fields: { name: string; type: string; description: string }[]; description: string; }

const kindColors: Record<string, string> = {
  type: "text-blue-600", input: "text-green-600", enum: "text-purple-600", interface: "text-orange-600",
};

export function GraphQLSchemaExplorer({ types }: { types: GqlType[] }) {
  const [selected, setSelected] = useState<string | null>(null);
  const active = types.find(t => t.name === selected);

  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">GraphQL Schema ({types.length} types)</h3>
      <div className="flex flex-wrap gap-1">
        {types.map(t => (
          <button key={t.name} onClick={() => setSelected(t.name)}
            className={`text-xs px-2.5 py-1 rounded-full border ${selected === t.name ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "border-gray-200 dark:border-gray-700"}`}>
            <span className={kindColors[t.kind] || ""}>{t.kind}</span> {t.name}
          </button>
        ))}
      </div>
      {active && (
        <div className="border dark:border-gray-700 rounded-xl p-4 bg-gray-50 dark:bg-gray-800/50">
          <div className="flex items-center gap-2 mb-2">
            <span className={`text-xs font-bold ${kindColors[active.kind] || ""}`}>{active.kind}</span>
            <span className="font-bold">{active.name}</span>
          </div>
          {active.description && <p className="text-xs text-gray-500 mb-2">{active.description}</p>}
          <div className="space-y-1 font-mono text-xs">
            {active.fields.map(f => (
              <div key={f.name} className="flex justify-between">
                <span>{f.name}</span>
                <span className="text-blue-500">{f.type}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
