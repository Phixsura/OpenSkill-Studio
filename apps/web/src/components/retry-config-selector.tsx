"use client";

interface RetryPolicy { name: string; maxRetries: number; strategy: string; }
interface RetryConfigSelectorProps { policies: RetryPolicy[]; selected: string;
  onSelect: (name: string) => void; }

export function RetryConfigSelector({ policies, selected, onSelect }: RetryConfigSelectorProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔁 Retry Policy</h3>
      <div className="grid grid-cols-2 gap-2">
        {policies.map(p => (
          <button key={p.name} onClick={() => onSelect(p.name)}
            className={`rounded-lg p-3 text-left border-2 transition ${
              p.name === selected ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" :
              "border-transparent bg-gray-50 dark:bg-gray-800 hover:border-gray-200"
            }`}>
            <p className="text-sm font-medium capitalize">{p.name}</p>
            <p className="text-xs text-gray-400">{p.maxRetries} retries · {p.strategy}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
