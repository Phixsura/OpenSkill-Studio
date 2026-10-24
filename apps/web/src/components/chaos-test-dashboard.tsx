"use client";

interface ResilienceResult { resilience_score: number; grade: string; error_spike_pct: number;
  latency_spike_ms: number; recovery_time_sec: number; fully_recovered: boolean; }
interface ChaosTestDashboardProps { experimentName: string; faultType: string;
  result: ResilienceResult; onRerun: () => void; }

const gradeColor: Record<string, string> = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", F: "text-red-600" };

export function ChaosTestDashboard({ experimentName, faultType, result, onRerun }: ChaosTestDashboardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Chaos Test Results</h2>
          <p className="text-xs text-gray-400">{experimentName} · {faultType}</p>
        </div>
        <span className={`text-4xl font-black ${gradeColor[result.grade] ?? ""}`}>{result.grade}</span>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-lg font-bold">{result.resilience_score}</p>
          <p className="text-xs text-gray-400">Score</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-lg font-bold">{result.error_spike_pct}%</p>
          <p className="text-xs text-gray-400">Error Spike</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-lg font-bold">{result.latency_spike_ms}ms</p>
          <p className="text-xs text-gray-400">Latency Spike</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-lg font-bold">{result.recovery_time_sec}s</p>
          <p className="text-xs text-gray-400">Recovery</p>
        </div>
      </div>
      <div className="flex items-center justify-between rounded border p-3 dark:border-gray-700">
        <span className="text-sm">{result.fully_recovered ? "✅ Fully recovered" : "⚠️ Did not fully recover"}</span>
        <button onClick={onRerun} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Re-run Test</button>
      </div>
    </div>
  );
}
