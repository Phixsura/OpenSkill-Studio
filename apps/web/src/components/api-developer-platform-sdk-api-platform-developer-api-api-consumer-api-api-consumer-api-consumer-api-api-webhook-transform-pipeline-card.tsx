"use client";

interface Step { id: string; type: string; order: number; enabled: boolean; }
interface PipelineInfo { id: string; webhookId: string; steps: Step[]; }
interface Props { pipelines: PipelineInfo[]; consumerId: string; appName: string; }

const typeColors: Record<string, string> = {
  filter: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  map: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  enrich: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  redact: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiWebhookTransformPipelineCard({ pipelines, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔧 Transform Pipelines</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {pipelines.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No pipelines</p>
      ) : (
        <div className="space-y-2">
          {pipelines.map((p) => (
            <div key={p.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{p.webhookId} — {p.steps.length} steps</div>
              <div className="mt-1 flex gap-1">
                {p.steps.map((s) => (
                  <span key={s.id} className={`rounded px-1 py-0.5 text-[9px] ${!s.enabled ? "opacity-50" : ""} ${typeColors[s.type] ?? "bg-gray-200 text-gray-600"}`}>{s.type}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
