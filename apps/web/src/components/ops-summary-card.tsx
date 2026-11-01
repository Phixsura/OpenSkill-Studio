"use client";

interface OpsSummaryCardProps { uptimePct: number; deploysToday: number;
  openIncidents: number; errorRate: number; changes24h: number;
  riskLevel: string; status: string; }

const RISK_COLORS: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-red-600",
};

export function OpsSummaryCard({ uptimePct, deploysToday, openIncidents, errorRate, changes24h, riskLevel, status }: OpsSummaryCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Ops Summary</h3>
        <span className={`text-xs font-medium capitalize ${RISK_COLORS[riskLevel] ?? ""}`}>{status} · {riskLevel} risk</span>
      </div>
      <div className="grid grid-cols-5 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Uptime", v: `${uptimePct}%` }, { l: "Deploys", v: deploysToday },
          { l: "Incidents", v: openIncidents }, { l: "Errors", v: `${errorRate}%` },
          { l: "Changes", v: changes24h }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
