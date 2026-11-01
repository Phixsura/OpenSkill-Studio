"use client";

interface StageInfo { stage: string; count: number; }
interface Props { stages: StageInfo[]; conversionRate: number; biggestDropoff: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformApiDeveloperEngagementFunnelCard({ stages, conversionRate, biggestDropoff, appName }: Props) {
  const maxCount = Math.max(1, ...stages.map(s => s.count));
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔽 Engagement Funnel</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-blue-600">{conversionRate}% end-to-end</span>
      </div>
      <div className="space-y-1.5">
        {stages.map((s) => (
          <div key={s.stage}>
            <div className="flex items-center justify-between text-[11px]">
              <span className={`text-gray-700 dark:text-gray-300 ${s.stage === biggestDropoff ? "text-red-500 font-bold" : ""}`}>{s.stage.replace(/_/g, " ")}</span>
              <span className="text-gray-400">{s.count.toLocaleString()}</span>
            </div>
            <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
              <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${(s.count / maxCount) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
      {biggestDropoff && <p className="mt-2 text-[10px] text-red-500">Biggest drop-off: {biggestDropoff.replace(/_/g, " ")}</p>}
    </div>
  );
}
