"use client";

interface SatInfo { nps_score: number; csat_score: number; total_responses: number; promoters: number; passives: number; detractors: number; sentiment: string; }
interface Props { satisfaction: SatInfo; appName: string; }

const sentColor: Record<string, string> = { excellent: "text-green-600", good: "text-blue-600", needs_improvement: "text-yellow-600", critical: "text-red-500" };

export default function APIDeveloperSatisfactionCard({ satisfaction: s, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">😊 Dev Satisfaction</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className={`text-lg font-bold ${sentColor[s.sentiment] ?? "text-gray-500"}`}>{s.nps_score}</span>
          <p className="text-[10px] text-gray-400">NPS</p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        {[
          { l: "CSAT", v: `${s.csat_score}/5` },
          { l: "Responses", v: s.total_responses },
          { l: "Promoters", v: s.promoters },
          { l: "Passives", v: s.passives },
          { l: "Detractors", v: s.detractors },
          { l: "Sentiment", v: s.sentiment.replace("_", " ") },
        ].map((m) => (
          <div key={m.l} className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-xs font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[7px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
