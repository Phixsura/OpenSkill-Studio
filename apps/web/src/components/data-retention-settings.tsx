"use client";

interface Policy { data_type: string; retention_days: number; category: string; is_custom: boolean; }
interface DataRetentionSettingsProps { policies: Policy[]; onUpdate: (dataType: string, days: number) => void; }

const categoryIcons: Record<string, string> = {
  analytics: "📊", operations: "⚙️", debugging: "🐛", compliance: "📋", infrastructure: "🏗️",
};

export function DataRetentionSettings({ policies, onUpdate }: DataRetentionSettingsProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Data Retention</h2>
      <div className="space-y-2">
        {policies.map(p => (
          <div key={p.data_type} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span>{categoryIcons[p.category] ?? "📁"}</span>
              <div>
                <p className="text-sm font-medium">{p.data_type.replace(/_/g, " ")}</p>
                <p className="text-xs text-gray-400">{p.category}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <select value={p.retention_days} onChange={e => onUpdate(p.data_type, Number(e.target.value))}
                className="rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-700">
                <option value={30}>30 days</option>
                <option value={90}>90 days</option>
                <option value={180}>180 days</option>
                <option value={365}>1 year</option>
                <option value={730}>2 years</option>
              </select>
              {p.is_custom && <span className="text-xs text-blue-500">Custom</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
