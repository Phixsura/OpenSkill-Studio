"use client";
export function FleetAiDepGraphPanel({ graphs, active, services, edges, circular }: { graphs: number; active: number; services: number; edges: number; circular: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ AI Dependency Graph</h3>
    <div className="text-sm">{active}/{graphs} active · {services} services · {edges} edges · {circular} circular</div>
  </div>);
}
