"use client";

interface OnboardingInfo {
  developer_id: string;
  completion_pct: number;
  completed_count: number;
  total_steps: number;
  is_complete: boolean;
}

interface APIDeveloperOnboardingCardProps {
  developers: OnboardingInfo[];
  completionRate: number;
  steps: string[];
  appName: string;
}

export default function APIDeveloperOnboardingCard({ developers, completionRate, steps, appName }: APIDeveloperOnboardingCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎓 Dev Onboarding</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {steps.length} steps</p>
        </div>
        <span className={`text-sm font-bold ${completionRate >= 80 ? "text-green-600" : "text-yellow-600"}`}>{completionRate}%</span>
      </div>

      {developers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No developers onboarding</p>
      ) : (
        <div className="space-y-1.5">
          {developers.map((d) => (
            <div key={d.developer_id}>
              <div className="flex justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{d.developer_id}</span>
                <span className="text-gray-400">{d.completed_count}/{d.total_steps} {d.is_complete ? "✓" : ""}</span>
              </div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1 rounded-full ${d.is_complete ? "bg-green-500" : "bg-blue-500"}`} style={{ width: `${d.completion_pct}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
