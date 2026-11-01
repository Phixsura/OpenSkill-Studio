"use client";

interface StepInfo {
  step_id: string;
  name: string;
  completed: boolean;
  required: boolean;
}

interface OnboardingTrackerCardProps {
  steps: StepInfo[];
  completionPct: number;
  isComplete: boolean;
  userId: string;
  appName: string;
}

export default function OnboardingTrackerCard({
  steps,
  completionPct,
  isComplete,
  userId,
  appName,
}: OnboardingTrackerCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Onboarding</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {userId}
          </p>
        </div>
        {isComplete ? (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            ✓ Complete
          </span>
        ) : (
          <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
            {completionPct.toFixed(0)}%
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div className="mb-4 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className={`h-2 rounded-full ${isComplete ? "bg-green-500" : "bg-blue-500"}`}
          style={{ width: `${completionPct}%` }}
        />
      </div>

      {/* Step checklist */}
      <div className="space-y-1.5">
        {steps.map((s) => (
          <div key={s.step_id} className="flex items-center gap-2">
            <span
              className={`text-sm ${s.completed ? "text-green-600 dark:text-green-400" : "text-gray-300 dark:text-gray-600"}`}
            >
              {s.completed ? "✓" : "○"}
            </span>
            <span
              className={`text-sm ${s.completed ? "text-gray-500 line-through" : "text-gray-800 dark:text-gray-200"}`}
            >
              {s.name}
            </span>
            {!s.required && <span className="text-[10px] text-gray-400">optional</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
