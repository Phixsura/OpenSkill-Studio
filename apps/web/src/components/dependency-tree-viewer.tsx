"use client";

interface DependencyTreeViewerProps { installOrder: string[]; unresolved: string[]; canInstall: boolean; }

export function DependencyTreeViewer({ installOrder, unresolved, canInstall }: DependencyTreeViewerProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Dependencies</h3>
        <span className={`text-xs font-medium ${canInstall ? "text-green-600" : "text-red-600"}`}>
          {canInstall ? "✅ All resolved" : "❌ Missing dependencies"}
        </span>
      </div>
      {installOrder.length > 0 && (
        <div className="mt-3">
          <p className="text-xs font-medium text-gray-500">Install Order</p>
          <ol className="mt-1 list-inside list-decimal text-sm">
            {installOrder.map(d => <li key={d} className="font-mono text-xs">{d}</li>)}
          </ol>
        </div>
      )}
      {unresolved.length > 0 && (
        <div className="mt-3">
          <p className="text-xs font-medium text-red-500">Missing</p>
          <ul className="mt-1 space-y-0.5">
            {unresolved.map(d => <li key={d} className="text-xs text-red-600">❌ {d}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
