"use client";

interface GateCheck { name: string; type: string; status: string; }
interface ReleaseGateCardProps { name: string; checks: GateCheck[];
  canRelease: boolean; passed: number; failed: number; total: number; }

export function ReleaseGateCard({ name, checks, canRelease, passed, failed, total }: ReleaseGateCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${canRelease ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold text-sm">🚦 Release Gate: {name}</h3>
        <span className={`text-xs font-medium ${canRelease ? "text-green-600" : "text-red-500"}`}>
          {canRelease ? "✅ Ready" : "🚫 Blocked"} · {passed}/{total}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {checks.map(c => (
          <div key={c.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span>{c.status === "passed" ? "✅" : c.status === "failed" ? "❌" : "⬜"}</span>
              <span className="font-medium">{c.name}</span>
              <span className="text-gray-400">{c.type}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
