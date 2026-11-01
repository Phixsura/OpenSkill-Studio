"use client";
export function FleetAiGnnPanel({ models, active, nodes, edges, accuracy }: { models: number; active: number; nodes: number; edges: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🕸️ AI Graph Neural Net</h3>
    <div className="text-sm">{active}/{models} active · {nodes.toLocaleString()} nodes · {edges.toLocaleString()} edges · {accuracy}% acc</div>
  </div>);
}
