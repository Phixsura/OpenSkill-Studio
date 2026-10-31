"use client";

interface DepResult { name: string; required: string; installed: string | null; status: string; }
interface DepCheckCardProps { dependencies: DepResult[]; allSatisfied: boolean; missingCount: number; }

const STATUS_ICON: Record<string, string> = { ok: "✅", missing: "❌", incompatible: "⚠️" };

export function DepCheckCard({ dependencies, allSatisfied, missingCount }: DepCheckCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">📋 Dependencies</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full ${allSatisfied ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
          {allSatisfied ? "✅ All satisfied" : `${missingCount} missing`}
        </span>
      </div>
      <div className="space-y-1">
        {dependencies.map(d => (
          <div key={d.name} className="flex items-center justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded px-3 py-1.5">
            <div className="flex items-center gap-2">
              <span>{STATUS_ICON[d.status] || "❓"}</span>
              <span className="font-mono text-xs">{d.name}</span>
            </div>
            <span className="text-xs text-gray-400">
              {d.installed ? `v${d.installed}` : "not installed"} {d.required !== "*" ? `(needs ${d.required})` : ""}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
