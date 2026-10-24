"use client";
export function FleetAiNerPanel({ extractors, active, docs, entities, types, f1 }: { extractors: number; active: number; docs: number; entities: number; types: number; f1: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏷️ AI NER</h3>
    <div className="text-sm">{active}/{extractors} active · {docs.toLocaleString()} docs · {entities.toLocaleString()} entities · {types} types · F1 {f1}</div>
  </div>);
}
