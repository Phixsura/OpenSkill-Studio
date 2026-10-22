"use client";

interface Node { id: string; name: string; }
interface Edge { from: string; to: string; type: string; }
interface DependencyGraphViewProps { nodes: Node[]; edges: Edge[]; }

export function DependencyGraphView({ nodes, edges }: DependencyGraphViewProps) {
  const nodeMap = Object.fromEntries(nodes.map(n => [n.id, n]));
  if (nodes.length === 0) return <p className="text-sm text-gray-400">No dependencies.</p>;

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Dependency Graph</h3>
      <p className="mt-1 text-xs text-gray-400">{nodes.length} apps · {edges.length} connections</p>
      <ul className="mt-3 space-y-2">
        {edges.map((e, i) => (
          <li key={i} className="flex items-center gap-2 text-sm">
            <span className="font-medium">{nodeMap[e.from]?.name || e.from}</span>
            <span className={e.type === "conflicts" ? "text-red-500" : "text-blue-500"}>
              {e.type === "conflicts" ? "⚡ conflicts" : "→ depends on"}
            </span>
            <span className="font-medium">{nodeMap[e.to]?.name || e.to}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
