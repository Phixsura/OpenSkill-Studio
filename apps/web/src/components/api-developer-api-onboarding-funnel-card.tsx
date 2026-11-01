"use client";

interface StageInfo { stage_name: string; entered: number; completed: number; conversion_rate: number; }
interface Props { stages: StageInfo[]; overallConversion: number; appName: string; }

export default function APIDeveloperAPIOnboardingFunnelCard({ stages, overallConversion, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔻 Onboarding Funnel</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{overallConversion}% overall</span>
      </div>
      {stages.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No funnel data</p>
      ) : (
        <div className="space-y-2">
          {stages.map((s, i) => {
            const widthPct = stages[0].entered > 0 ? Math.round((s.entered / stages[0].entered) * 100) : 0;
            return (
              <div key={s.stage_name}>
                <div className="flex justify-between text-[11px]">
                  <span className="text-gray-700 dark:text-gray-300">{s.stage_name}</span>
                  <span className="text-gray-400">{s.completed}/{s.entered} ({s.conversion_rate}%)</span>
                </div>
                <div className="mt-0.5 h-2 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                  <div className="h-2 rounded-full bg-blue-500" style={{ width: `${widthPct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
