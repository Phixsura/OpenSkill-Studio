"use client";
interface Gate { name: string; passed: boolean; required: boolean; }
interface ReleaseGatePanelProps { release: string; gates: Gate[]; canRelease: boolean; passedCount: number; }
export function ReleaseGatePanel({ release, gates, canRelease, passedCount }: ReleaseGatePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Release Gates: {release}</h3>
        <span className={`text-xs font-bold ${canRelease ? "text-green-600" : "text-red-500"}`}>
          {canRelease ? "✅ Ready" : "❌ Blocked"} · {passedCount}/{gates.length}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {gates.map(g => (
          <div key={g.name} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span>{g.passed ? "✅" : "❌"}</span>
              <span className={!g.passed && g.required ? "text-red-600 font-bold" : ""}>{g.name}</span>
            </div>
            <span className="text-gray-400">{g.required ? "required" : "optional"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
