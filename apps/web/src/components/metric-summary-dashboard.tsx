"use client";

interface Kpi { label: string; value: number; display: string; icon: string; }
interface MetricSummaryDashboardProps { appName: string; period: string;
  kpis: Kpi[]; healthScore: number; healthGrade: string; }

const gradeColors: Record<string, string> = {
  A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", F: "text-red-600",
};

export function MetricSummaryDashboard({ appName, period, kpis, healthScore, healthGrade }: MetricSummaryDashboardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold">{appName}</h3>
          <p className="text-xs text-gray-400">{period} metrics</p>
        </div>
        <div className="text-right">
          <span className={`text-3xl font-bold ${gradeColors[healthGrade] ?? ""}`}>{healthGrade}</span>
          <p className="text-xs text-gray-400">{healthScore}/100</p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {kpis.map(k => (
          <div key={k.label} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <span>{k.icon}</span>
            <p className="text-lg font-bold mt-1">{k.display}</p>
            <p className="text-xs text-gray-400">{k.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
