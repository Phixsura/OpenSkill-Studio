"use client";

interface RetentionPolicy { type: string; description: string; retention: string; autoDelete: boolean; }
interface DataRetentionPanelProps { policies: RetentionPolicy[]; autoDeleteCount: number; }

export function DataRetentionPanel({ policies, autoDeleteCount }: DataRetentionPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Data Retention</h3>
        <span className="text-xs text-gray-400">{autoDeleteCount} auto-delete policies</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {policies.map(p => (
          <div key={p.type} className="flex items-center justify-between px-4 py-3">
            <div>
              <p className="text-sm font-medium capitalize">{p.type}</p>
              <p className="text-xs text-gray-400">{p.description}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm">{p.retention}</span>
              {p.autoDelete ? (
                <span className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">auto</span>
              ) : (
                <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">manual</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
