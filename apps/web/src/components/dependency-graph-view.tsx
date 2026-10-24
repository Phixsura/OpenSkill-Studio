"use client";

interface Node { id: string; name: string; type: string; version?: string; }
interface Edge { from: string; to: string; kind: string; }
interface DependencyGraphViewProps { appName: string; nodes: Node[]; edges: Edge[]; totalDependencies: number; }

export function DependencyGraphView({ appName, nodes, edges, totalDependencies }: DependencyGraphViewProps) {
  const root = nodes.find(n => n.type === "root");
  const deps = nodes.filter(n => n.type === "dependency");
  const transitive = nodes.filter(n => n.type === "transitive");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Dependencies</h2>
        <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium dark:bg-gray-800">
          {totalDependencies} total
        </span>
      </div>
      <div className="rounded-lg border p-4 dark:border-gray-700">
        <p className="text-center font-bold">{root?.name ?? appName}</p>
        {deps.length > 0 && (
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            {deps.map(d => {
              const children = edges.filter(e => e.from === d.id).map(e => nodes.find(n => n.id === e.to)!).filter(Boolean);
              return (
                <div key={d.id} className="rounded border p-2 dark:border-gray-600">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-blue-500" />
                    <span className="text-sm font-medium">{d.name}</span>
                    {d.version && <span className="text-xs text-gray-400">v{d.version}</span>}
                  </div>
                  {children.length > 0 && (
                    <div className="ml-4 mt-1 space-y-0.5">
                      {children.map(c => (
                        <p key={c.id} className="text-xs text-gray-400">↳ {c.name}</p>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
        {deps.length === 0 && <p className="mt-2 text-center text-sm text-gray-400">No dependencies</p>}
      </div>
    </div>
  );
}
