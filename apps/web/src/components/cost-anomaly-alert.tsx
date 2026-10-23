"use client";

interface CostAnomaly { date: string; amount: number; expected: number;
  deviationPct: number; service: string; display: string; }
interface CostAnomalyAlertProps { anomalies: CostAnomaly[];
  meanDaily: number; totalDisplay: string; hasAnomalies: boolean; }

export function CostAnomalyAlert({ anomalies, meanDaily, totalDisplay, hasAnomalies }: CostAnomalyAlertProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">💸 Cost Anomalies</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          hasAnomalies ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
        }`}>{hasAnomalies ? `⚠️ ${anomalies.length} spikes` : "✅ Normal"}</span>
      </div>
      <div className="flex gap-4 text-sm mb-4">
        <span>Avg daily: <strong>${meanDaily.toFixed(0)}</strong></span>
        <span>Total: <strong>{totalDisplay}</strong></span>
      </div>
      {anomalies.length > 0 && (
        <div className="space-y-2">
          {anomalies.map(a => (
            <div key={a.date} className="bg-red-50 dark:bg-red-900/10 rounded-lg px-4 py-3">
              <div className="flex justify-between text-sm">
                <span className="font-medium">{a.date}</span>
                <span className="text-red-600 font-bold">{a.display}</span>
              </div>
              <p className="text-xs text-gray-400 mt-0.5">
                Expected ~${a.expected.toFixed(0)} · {a.service}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
