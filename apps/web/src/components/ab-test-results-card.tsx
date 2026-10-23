"use client";

interface TestArm { rate: number; visitors: number; conversions: number; }
interface AbTestResultsCardProps { control: TestArm; variant: TestArm; liftPct: number;
  winner: string; significant: boolean; recommendation: string; onPromote: () => void; }

export function AbTestResultsCard({ control, variant, liftPct, winner, significant, recommendation, onPromote }: AbTestResultsCardProps) {
  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <h2 className="text-lg font-semibold">A/B Test Results</h2>
      <div className="grid grid-cols-2 gap-4">
        {[
          { label: "Control", arm: control, active: winner === "control" },
          { label: "Variant", arm: variant, active: winner === "variant" },
        ].map(a => (
          <div key={a.label} className={`rounded-lg border p-4 text-center ${a.active ? "border-green-500 bg-green-50 dark:bg-green-900/10" : "dark:border-gray-700"}`}>
            <p className="text-sm font-medium">{a.label} {a.active && "🏆"}</p>
            <p className="mt-2 text-3xl font-black">{a.arm.rate}%</p>
            <p className="text-xs text-gray-400">{a.arm.conversions.toLocaleString()} / {a.arm.visitors.toLocaleString()}</p>
          </div>
        ))}
      </div>
      <div className="text-center">
        <p className={`text-lg font-bold ${liftPct > 0 ? "text-green-600" : "text-red-600"}`}>
          {liftPct > 0 ? "↑" : "↓"} {Math.abs(liftPct)}% lift
        </p>
        <p className={`text-xs ${significant ? "text-green-500" : "text-yellow-500"}`}>
          {significant ? "✅ Statistically significant" : "⏳ Not yet significant"}
        </p>
        <p className="mt-1 text-sm text-gray-400">{recommendation}</p>
      </div>
      {significant && winner === "variant" && (
        <button onClick={onPromote} className="w-full rounded bg-green-600 py-2 text-sm font-medium text-white">
          Promote Variant
        </button>
      )}
    </div>
  );
}
