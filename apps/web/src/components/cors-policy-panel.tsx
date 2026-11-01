"use client";

interface CorsPolicy { origin: string; methods: string[]; credentials: boolean; maxAge: number; }
interface CorsPolicyPanelProps { policies: CorsPolicy[]; }

export function CorsPolicyPanel({ policies }: CorsPolicyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔓 CORS Policies</h3>
        <span className="text-xs text-gray-400">{policies.length} origins</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {policies.map(p => (
          <div key={p.origin} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono font-semibold">{p.origin}</span>
              <span className="text-gray-400">{p.maxAge}s</span>
            </div>
            <div className="text-gray-400">
              {p.methods.join(", ")}{p.credentials ? " · 🔑 credentials" : ""}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
