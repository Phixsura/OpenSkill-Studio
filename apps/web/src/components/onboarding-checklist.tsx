"use client";

interface ChecklistStep {
  step_id: string;
  title: string;
  description: string;
  required: boolean;
  status: "pending" | "completed" | "skipped";
}

interface ChecklistProgress {
  total_steps: number;
  completed: number;
  progress_pct: number;
  can_publish: boolean;
}

interface OnboardingChecklistProps {
  appName: string;
  steps: ChecklistStep[];
  progress: ChecklistProgress;
  onComplete: (stepId: string) => void;
  onSkip: (stepId: string) => void;
}

const STATUS_ICONS: Record<string, { icon: string; color: string }> = {
  completed: { icon: "✓", color: "text-green-600 bg-green-100 dark:bg-green-900/20" },
  skipped: { icon: "—", color: "text-gray-400 bg-gray-100 dark:bg-gray-800" },
  pending: { icon: "○", color: "text-gray-400 bg-gray-100 dark:bg-gray-800" },
};

export function OnboardingChecklist({
  appName,
  steps,
  progress,
  onComplete,
  onSkip,
}: OnboardingChecklistProps) {
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold">Getting Started</h3>
            <p className="text-xs text-gray-500">{appName}</p>
          </div>
          <span className="text-sm font-bold">{progress.progress_pct}%</span>
        </div>
        <div className="mt-2 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div
            className={`h-full rounded-full transition-all ${progress.can_publish ? "bg-green-500" : "bg-blue-500"}`}
            style={{ width: `${progress.progress_pct}%` }}
          />
        </div>
        {progress.can_publish && (
          <p className="mt-1 text-[10px] font-medium text-green-600">✓ Ready to publish</p>
        )}
      </div>

      {/* Steps */}
      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {steps.map((step, i) => {
          const st = STATUS_ICONS[step.status] ?? STATUS_ICONS.pending;
          const isPending = step.status === "pending";
          return (
            <div
              key={step.step_id}
              className={`flex items-start gap-3 px-4 py-3 ${!isPending ? "opacity-60" : ""}`}
            >
              <span
                className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${st.color}`}
              >
                {step.status === "pending" ? i + 1 : st.icon}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className={`text-sm ${isPending ? "font-medium" : ""}`}>{step.title}</span>
                  {step.required && <span className="text-[9px] text-red-500">required</span>}
                </div>
                <p className="text-xs text-gray-500">{step.description}</p>
                {isPending && (
                  <div className="mt-1.5 flex gap-1.5">
                    <button
                      onClick={() => onComplete(step.step_id)}
                      className="rounded bg-blue-600 px-2.5 py-1 text-[10px] font-medium text-white hover:bg-blue-700"
                    >
                      Complete
                    </button>
                    {!step.required && (
                      <button
                        onClick={() => onSkip(step.step_id)}
                        className="rounded border border-gray-300 px-2.5 py-1 text-[10px] text-gray-500 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-800"
                      >
                        Skip
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
