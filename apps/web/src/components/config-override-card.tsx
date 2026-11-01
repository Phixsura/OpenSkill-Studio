"use client";

interface LayerInfo {
  layer_id: string;
  priority: number;
  key_count: number;
}

interface ResolvedConfig {
  [key: string]: unknown;
}

interface ConfigOverrideCardProps {
  layers: LayerInfo[];
  resolved: ResolvedConfig;
  appName: string;
}

export default function ConfigOverrideCard({ layers, resolved, appName }: ConfigOverrideCardProps) {
  const keys = Object.keys(resolved).sort();

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Config Layers</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {layers.length} layers · {keys.length} keys
        </span>
      </div>

      {/* Layers */}
      <div className="mb-3 flex flex-wrap gap-1.5">
        {layers.map((l, i) => (
          <span
            key={l.layer_id}
            className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
              i === 0
                ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
            }`}
          >
            {l.layer_id} (p{l.priority}) · {l.key_count} keys
          </span>
        ))}
      </div>

      {/* Resolved config */}
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No configuration</p>
      ) : (
        <div className="rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
          <p className="mb-1.5 text-[10px] font-medium uppercase tracking-wider text-gray-500">
            Resolved
          </p>
          <div className="space-y-0.5">
            {keys.map((k) => (
              <div key={k} className="flex items-center justify-between font-mono text-[11px]">
                <span className="text-gray-600 dark:text-gray-400">{k}</span>
                <span className="text-gray-800 dark:text-gray-200">
                  {JSON.stringify(resolved[k])}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
