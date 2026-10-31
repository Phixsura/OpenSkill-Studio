"use client";

interface RetentionPreset { id: string; label: string; maxDays: number; }
interface DataRetentionConfigProps { presets: RetentionPreset[]; currentPreset: string;
  config: Record<string, number>; onPreset: (id: string) => void; }

export function DataRetentionConfig({ presets, currentPreset, config, onPreset }: DataRetentionConfigProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">📅 Data Retention</h3>
      <div className="flex gap-2 mb-4">
        {presets.map(p => (
          <button key={p.id} onClick={() => onPreset(p.id)}
            className={`text-xs px-3 py-1.5 rounded-lg capitalize ${
              p.id === currentPreset ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"
            }`}>{p.label}</button>
        ))}
      </div>
      <div className="space-y-2">
        {Object.entries(config).map(([key, days]) => (
          <div key={key} className="flex justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded px-3 py-2">
            <span className="capitalize">{key.replace("_", " ")}</span>
            <span className="text-gray-400">{days} days</span>
          </div>
        ))}
      </div>
    </div>
  );
}
