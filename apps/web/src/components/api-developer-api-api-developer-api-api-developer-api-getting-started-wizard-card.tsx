"use client";

interface ProgressInfo { developer_id: string; completed_steps: string[]; current_step: string; progress_pct: number; is_complete: boolean; }
interface Props { progress: ProgressInfo; completionRate: number; appName: string; }

const STEPS = ["create_account", "generate_api_key", "make_first_call", "configure_webhook", "go_live"];
const stepLabel: Record<string, string> = { create_account: "Create Account", generate_api_key: "Generate Key", make_first_call: "First Call", configure_webhook: "Webhooks", go_live: "Go Live" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiGettingStartedWizardCard({ progress: p, completionRate, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚀 Getting Started</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${p.is_complete ? "text-green-600" : "text-blue-600"}`}>{p.progress_pct}%</span>
      </div>
      <div className="mb-3 h-2 rounded-full bg-gray-100 dark:bg-gray-800">
        <div className={`h-2 rounded-full ${p.is_complete ? "bg-green-500" : "bg-blue-500"}`} style={{ width: `${p.progress_pct}%` }} />
      </div>
      <div className="space-y-1">
        {STEPS.map((step) => (
          <div key={step} className="flex items-center gap-2 text-[11px]">
            <span className={p.completed_steps.includes(step) ? "text-green-500" : step === p.current_step ? "text-blue-500" : "text-gray-300"}>
              {p.completed_steps.includes(step) ? "✓" : step === p.current_step ? "→" : "○"}
            </span>
            <span className={p.completed_steps.includes(step) ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}>
              {stepLabel[step] ?? step}
            </span>
          </div>
        ))}
      </div>
      <p className="mt-2 text-[10px] text-gray-400">{completionRate}% of developers completed</p>
    </div>
  );
}
