"use client";

interface InstallationConfigPanelProps {
  config: Record<string, unknown>;
  configSchema?: {
    properties?: Record<string, { type?: string; description?: string }>;
    required?: string[];
  };
  onSave?: (config: Record<string, unknown>) => void;
  readOnly?: boolean;
}

export function InstallationConfigPanel({ config, configSchema, onSave, readOnly }: InstallationConfigPanelProps) {
  const properties = configSchema?.properties ?? {};
  const required = new Set(configSchema?.required ?? []);
  const entries = Object.entries(properties);

  if (entries.length === 0 && Object.keys(config).length === 0) {
    return <p className="py-4 text-center text-sm text-gray-400">No configuration</p>;
  }

  return (
    <div className="space-y-3">
      {entries.length > 0 ? (
        entries.map(([key, schema]) => (
          <div key={key} className="rounded border border-gray-200 p-3 dark:border-gray-700">
            <label className="text-sm font-medium">
              {key}
              {required.has(key) && <span className="ml-1 text-red-500">*</span>}
            </label>
            {schema.description && (
              <p className="text-xs text-gray-500 dark:text-gray-400">{schema.description}</p>
            )}
            <div className="mt-1">
              <code className="rounded bg-gray-100 px-2 py-1 text-sm dark:bg-gray-800">
                {JSON.stringify(config[key] ?? "", null, 0)}
              </code>
            </div>
          </div>
        ))
      ) : (
        <pre className="rounded bg-gray-100 p-3 text-sm dark:bg-gray-800">
          {JSON.stringify(config, null, 2)}
        </pre>
      )}
    </div>
  );
}
