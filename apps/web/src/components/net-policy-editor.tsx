"use client";

interface NetRule { name: string; direction: string; action: string;
  source: string; destination: string; port: number; protocol: string; }
interface NetPolicyEditorProps { rules: NetRule[]; onAdd: () => void; onDelete: (name: string) => void; }

export function NetPolicyEditor({ rules, onAdd, onDelete }: NetPolicyEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔒 Network Policies</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{rules.length} rules</span>
          <button onClick={onAdd} className="px-2 py-0.5 text-xs bg-blue-500 text-white rounded">+ Add</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rules.map(r => (
          <div key={r.name} className="flex items-center justify-between px-4 py-2.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${r.action === "allow" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                {r.action}
              </span>
              <span className="capitalize text-gray-400">{r.direction}</span>
              <span className="font-mono">{r.source} → {r.destination}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <span>{r.protocol.toUpperCase()}:{r.port || "*"}</span>
              <button onClick={() => onDelete(r.name)} className="text-red-500">×</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
