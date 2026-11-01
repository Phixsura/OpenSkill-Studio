"use client";

interface Policy { name: string; effect: string; resource: string; actions: string[]; }
interface PermissionPolicyEditorProps { policies: Policy[]; onAdd: () => void; onRemove: (name: string) => void; }

export function PermissionPolicyEditor({ policies, onAdd, onRemove }: PermissionPolicyEditorProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🛡️ Permission Policies</h3>
        <button onClick={onAdd} className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">+ Add Policy</button>
      </div>
      <div className="space-y-2">
        {policies.map(p => (
          <div key={p.name} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <div className="flex items-center gap-2">
                <span className={`text-xs px-1.5 py-0.5 rounded font-bold ${p.effect === "allow" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{p.effect.toUpperCase()}</span>
                <span className="text-sm font-medium">{p.name}</span>
              </div>
              <p className="text-xs text-gray-400 mt-0.5">{p.resource} → {p.actions.join(", ")}</p>
            </div>
            <button onClick={() => onRemove(p.name)} className="text-xs text-red-500 hover:text-red-700">Remove</button>
          </div>
        ))}
      </div>
    </div>
  );
}
