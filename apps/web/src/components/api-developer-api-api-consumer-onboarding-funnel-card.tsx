"use client";

interface StepInfo { step: string; entered: number; completed: number; conversion_rate: number; }
interface Props { steps: StepInfo[]; overallConversion: number; appName: string; }

export default function APIDeveloperAPIApiConsumerOnboardingFunnelCard({ steps, overallConversion, appName }: Props) {
  const maxEntered = Math.max(1, ...steps.map(s => s.entered));
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔽 Onboarding Funnel</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-blue-600">{overallConversion}% end-to-end</span>
      </div>
      <div className="space-y-1.5">
        {steps.map((s) => (
          <div key={s.step}>
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.step.replace(/_/g, " ")}</span>
              <span className="text-gray-400">{s.completed}/{s.entered} ({s.conversion_rate}%)</span>
            </div>
            <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
              <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${(s.entered / maxEntered) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
