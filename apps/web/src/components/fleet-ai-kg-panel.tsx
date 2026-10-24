"use client";
export function FleetAiKgPanel({ graphs, active, entities, relations, queries }: { graphs: number; active: number; entities: number; relations: number; queries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ AI Knowledge Graph</h3>
    <div className="text-sm">{active}/{graphs} active · {entities.toLocaleString()} entities · {relations.toLocaleString()} relations · {queries.toLocaleString()} queries</div>
  </div>);
}
