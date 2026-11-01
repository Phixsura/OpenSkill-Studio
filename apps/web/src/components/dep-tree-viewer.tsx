"use client";

interface DepTreeViewerProps { roots: string[]; tree: Record<string, string[]>;
  maxDepth: number; edges: number; hasCycles: boolean; }

export function DepTreeViewer({ roots, tree, maxDepth, edges, hasCycles }: DepTreeViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌳 Dependency Tree</h3>
        <span className={`text-xs ${hasCycles ? "text-red-500" : "text-green-600"}`}>
          {roots.length} roots · depth {maxDepth} · {edges} edges{hasCycles ? " · ⚠ cycles" : ""}
        </span>
      </div>
      <div className="p-4 text-xs font-mono space-y-1">
        {roots.map(root => (
          <div key={root}>
            <div className="font-bold">{root}</div>
            {(tree[root] || []).map(child => (
              <div key={child} className="pl-4 text-gray-500">
                └─ {child}
                {(tree[child] || []).map(gc => (
                  <div key={gc} className="pl-4 text-gray-400">└─ {gc}</div>
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
