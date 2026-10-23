"use client";

interface ArmData { visitors: number; conversions: number; rate: number; rateDisplay: string; }
interface ABTestResultsCardProps {
  testName: string; control: ArmData; variant: ArmData;
  liftDisplay: string; significant: boolean; winner: string;
}

export function ABTestResultsCard({ testName, control, variant, liftDisplay, significant, winner }: ABTestResultsCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🧪 {testName}</h3>
      <div className="grid grid-cols-2 gap-4 mb-3">
        <div className={`rounded-lg p-3 text-center ${winner === "control" ? "bg-green-50 dark:bg-green-900/20 ring-2 ring-green-500" : "bg-gray-50 dark:bg-gray-800"}`}>
          <p className="text-xs text-gray-500 mb-1">Control</p>
          <p className="text-xl font-bold">{control.rateDisplay}</p>
          <p className="text-xs text-gray-400">{control.conversions.toLocaleString()} / {control.visitors.toLocaleString()}</p>
          {winner === "control" && <span className="text-xs text-green-600 font-medium">🏆 Winner</span>}
        </div>
        <div className={`rounded-lg p-3 text-center ${winner === "variant" ? "bg-green-50 dark:bg-green-900/20 ring-2 ring-green-500" : "bg-gray-50 dark:bg-gray-800"}`}>
          <p className="text-xs text-gray-500 mb-1">Variant</p>
          <p className="text-xl font-bold">{variant.rateDisplay}</p>
          <p className="text-xs text-gray-400">{variant.conversions.toLocaleString()} / {variant.visitors.toLocaleString()}</p>
          {winner === "variant" && <span className="text-xs text-green-600 font-medium">🏆 Winner</span>}
        </div>
      </div>
      <div className="flex justify-between text-sm">
        <span>Lift: <strong>{liftDisplay}</strong></span>
        <span className={significant ? "text-green-600" : "text-yellow-500"}>
          {significant ? "✅ Significant" : "⏳ Not significant"}
        </span>
      </div>
    </div>
  );
}
