"use client";
interface RcEvalPanelProps { version: string; verdict: string; checks: Record<string, boolean>; passed: number; total: number; }
const VERDICT_STYLE: Record<string, string> = { promote: "text-green-600", hold: "text-yellow-600", reject: "text-red-500" };
export function RcEvalPanel({ version, verdict, checks, passed, total }: RcEvalPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 RC Evaluation: {version}</h3>
        <span className={`text-sm font-bold uppercase ${VERDICT_STYLE[verdict] ?? ""}`}>{verdict} ({passed}/{total})</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(checks).map(([name, ok]) => (
          <div key={name} className="flex justify-between px-4 py-1.5 text-xs">
            <span>{name.replace(/_/g, " ")}</span>
            <span>{ok ? "✅" : "❌"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
