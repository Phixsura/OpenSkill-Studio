"use client";

interface HealthReportCardProps { score: number; grade: string;
  services: { total: number; healthy: number; degraded: number; down: number };
  incidents: { total: number; open: number };
  slaCompliance: number; uptimePct: number; recommendation: string; }

const GRADE_COLORS: Record<string, string> = {
  A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-orange-600", F: "text-red-600",
};

export function HealthReportCard({ score, grade, services, incidents, slaCompliance, uptimePct, recommendation }: HealthReportCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700">
        <div className={`text-5xl font-bold ${GRADE_COLORS[grade] ?? ""}`}>{grade}</div>
        <div className="text-lg font-mono mt-1">{score}/100</div>
        <div className="text-xs text-gray-400 mt-1">Platform Health Report</div>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Services", v: `${services.healthy}/${services.total}` },
          { l: "Uptime", v: `${uptimePct}%` },
          { l: "SLA", v: `${slaCompliance}%` },
          { l: "Incidents", v: `${incidents.open} open` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="p-3 text-xs text-gray-500">💡 {recommendation}</div>
    </div>
  );
}
