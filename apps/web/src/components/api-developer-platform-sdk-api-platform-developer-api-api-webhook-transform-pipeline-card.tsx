"use client";

interface StepInfo { step_id: string; transform_type: string; }
interface PipelineInfo { pipeline_id: string; consumer_id: string; steps: StepInfo[]; executions: number; }
interface Props { pipelines: PipelineInfo[]; appName: string; }

const stepIcon: Record<string, string> = { add_field: "➕", remove_field: "🗑️", rename_field: "✏️", wrap: "📦", flatten: "📄" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookTransformPipelineCard({ pipelines, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔧 Transform Pipelines</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {pipelines.length} pipelines</p>
      </div>
      {pipelines.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No pipelines configured</p>
      ) : (
        <div className="space-y-2">
          {pipelines.map((p) => (
            <div key={p.pipeline_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
                <span className="text-gray-400">{p.executions.toLocaleString()}×</span>
              </div>
              <div className="mt-0.5 flex gap-1">
                {p.steps.map((s) => <span key={s.step_id} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{stepIcon[s.transform_type] ?? "•"} {s.transform_type}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
