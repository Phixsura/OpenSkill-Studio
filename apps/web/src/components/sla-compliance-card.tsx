"use client";

interface SlaCheck { metric: string; actual: number; target: number; unit: string; passed: boolean; }
interface SlaComplianceCardProps { status: string; scoreDisplay: string; period: string;
  checks: SlaCheck[]; creditDue: boolean; }

const METRIC_LABEL: Record<string, string> = {
  uptime: "Uptime", avg_response: "Avg Response", p99_response: "P99 Response", incidents: "Incidents",
};

export function SlaComplianceCard({ status, scoreDisplay, period, checks, creditDue }: SlaComplianceCardProps) {
  return (
    <div className={`rounded-xl border p-5 ${status === "compliant" ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📊 SLA Compliance</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400 capitalize">{period}</span>
          <span className={`text-sm font-bold ${status === "compliant" ? "text-green-600" : "text-red-600"}`}>
            {scoreDisplay}
          </span>
        </div>
      </div>
      <div className="space-y-2">
        {checks.map(c => (
          <div key={c.metric} className="flex items-center justify-between text-sm">
            <span>{METRIC_LABEL[c.metric] || c.metric}</span>
            <div className="flex items-center gap-2">
              <span className="text-gray-500">{c.actual}{c.unit} / {c.target}{c.unit}</span>
              <span>{c.passed ? "✅" : "❌"}</span>
            </div>
          </div>
        ))}
      </div>
      {creditDue && (
        <div className="mt-3 p-2 bg-red-50 dark:bg-red-900/20 rounded text-xs text-red-600">
          ⚠️ SLA credit due — uptime target breached
        </div>
      )}
    </div>
  );
}
