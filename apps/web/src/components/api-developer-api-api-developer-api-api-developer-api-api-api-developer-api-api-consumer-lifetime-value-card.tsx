"use client";

interface ConsumerInfo { consumer_id: string; ltv_cents: number; arpu_cents: number; plan: string; churn_risk: string; months_active: number; }
interface Props { consumers: ConsumerInfo[]; totalMrrCents: number; atRiskCount: number; appName: string; }

function fmtCents(c: number) { return `$${(c / 100).toFixed(0)}`; }
const riskColor: Record<string, string> = { low: "text-green-600", medium: "text-yellow-600", high: "text-red-600" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiConsumerLifetimeValueCard({ consumers, totalMrrCents, atRiskCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💎 Consumer LTV</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · MRR: {fmtCents(totalMrrCents)}</p>
        </div>
        {atRiskCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{atRiskCount} at risk</span>}
      </div>
      {consumers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No consumer data</p>
      ) : (
        <div className="space-y-1.5">
          {consumers.slice(0, 5).map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              <div className="flex gap-2 text-[10px]">
                <span className="font-bold text-green-600">LTV: {fmtCents(c.ltv_cents)}</span>
                <span className={riskColor[c.churn_risk] ?? ""}>{c.churn_risk}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
