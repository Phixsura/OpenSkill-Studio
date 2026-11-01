"use client";

interface Variant { id: string; name: string; impressions: number; conversions: number; rate: number; }
interface TestResult { testId: string; field: string; variants: Variant[]; }

export function ABTestResultsCard({ result, onStop }: { result: TestResult; onStop?: (testId: string) => void }) {
  const winner = result.variants.reduce((a, b) => a.rate > b.rate ? a : b);
  return (
    <div className="border dark:border-gray-700 rounded-xl p-4 space-y-3">
      <div className="flex justify-between items-center">
        <div>
          <span className="font-bold text-sm">A/B Test: {result.field}</span>
          <span className="text-xs text-gray-500 ml-2">{result.testId}</span>
        </div>
        <button onClick={() => onStop?.(result.testId)} className="text-xs text-red-400">Stop Test</button>
      </div>
      <div className="space-y-2">
        {result.variants.map(v => {
          const isWinner = v.id === winner.id && v.impressions > 0;
          return (
            <div key={v.id} className={`rounded-lg p-3 ${isWinner ? "bg-green-50 border border-green-200 dark:bg-green-900/10 dark:border-green-800" : "bg-gray-50 dark:bg-gray-800"}`}>
              <div className="flex justify-between text-sm">
                <span className="font-medium">{v.name} {isWinner && "👑"}</span>
                <span className="font-bold">{v.rate}%</span>
              </div>
              <div className="flex gap-4 text-xs text-gray-500 mt-1">
                <span>{v.impressions} impressions</span>
                <span>{v.conversions} conversions</span>
              </div>
              <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full mt-1.5">
                <div className={`h-full rounded-full ${isWinner ? "bg-green-500" : "bg-blue-400"}`} style={{ width: `${Math.min(100, v.rate)}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
