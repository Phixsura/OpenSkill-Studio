"use client";

interface StepInfo { step_id: string; operation: string; }
interface PipelineInfo { pipeline_id: string; steps: StepInfo[]; execution_count: number; error_count: number; }
interface Props { pipelines: PipelineInfo[]; appName: string; }

const opIcon: Record<string, string> = { rename_field: "✏️", remove_field: "🗑️", add_field: "➕", map_value: "🔄" };

export default function APIDeveloperAPIWebhookTransformationPipelineCard({ pipelines, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔧 Transform Pipelines</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {pipelines.length} pipelines</p>
      </div>
      {pipelines.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No pipelines</p>
      ) : (
        <div className="space-y-2">
          {pipelines.map((p) => (
            <div key={p.pipeline_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{p.pipeline_id}</span>
                <span className="text-gray-400">{p.execution_count} runs</span>
              </div>
              <div className="mt-0.5 flex gap-1 text-[10px]">
                {p.steps.map((s) => (
                  <span key={s.step_id} className="rounded bg-blue-50 px-1 py-0.5 text-blue-700 dark:bg-blue-900 dark:text-blue-200">{opIcon[s.operation] ?? "•"} {s.operation}</span>
                ))}
              </div>
              {p.error_count > 0 && <p className="mt-0.5 text-[10px] text-red-500">{p.error_count} errors</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
