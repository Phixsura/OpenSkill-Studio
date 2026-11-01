"use client";

interface CorsPolicyEditorProps { origins: string[]; methods: string[];
  credentials: boolean; maxAge: number;
  onAddOrigin: (origin: string) => void; onRemoveOrigin: (origin: string) => void; }

export function CorsPolicyEditor({ origins, methods, credentials, maxAge, onAddOrigin, onRemoveOrigin }: CorsPolicyEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 CORS Policy</h3>
      </div>
      <div className="p-4 space-y-3">
        <div>
          <div className="text-xs text-gray-400 mb-1">Allowed Origins</div>
          <div className="flex flex-wrap gap-1">
            {origins.map(o => (
              <span key={o} className="inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded">
                {o}
                <button onClick={() => onRemoveOrigin(o)} className="text-blue-400 hover:text-red-500">×</button>
              </span>
            ))}
            <button onClick={() => onAddOrigin("")} className="px-2 py-0.5 text-xs text-blue-500 border border-dashed border-blue-300 rounded">+ Add</button>
          </div>
        </div>
        <div className="flex gap-4 text-xs">
          <div><span className="text-gray-400">Methods:</span> {methods.join(", ")}</div>
          <div><span className="text-gray-400">Credentials:</span> {credentials ? "Yes" : "No"}</div>
          <div><span className="text-gray-400">Max-Age:</span> {maxAge}s</div>
        </div>
      </div>
    </div>
  );
}
