"use client";
export function FleetAiKgPanel({ graphs, active, entities, relationships, queries }: { graphs: number; active: number; entities: number; relationships: number; queries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ AI Knowledge Graph</h3>
    <div className="text-sm">{active}/{graphs} active · {entities.toLocaleString()} entities · {relationships.toLocaleString()} rels</div>
  </div>);
}
