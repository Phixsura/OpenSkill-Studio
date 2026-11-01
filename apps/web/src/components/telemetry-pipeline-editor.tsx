"use client";

interface Pipeline { pipeline_id: string; name: string; sources: string[]; destinations: string[]; status: string; }
interface TelemetryPipelineEditorProps { pipelines: Pipeline[];
  onToggle: (id: string) => void; onDelete: (id: string) => void; onCreate: () => void; }

export function TelemetryPipelineEditor({ pipelines, onToggle, onDelete, onCreate }: TelemetryPipelineEditorProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Telemetry Pipelines</h2>
        <button onClick={onCreate} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">New Pipeline</button>
      </div>
      {pipelines.map(p => (
        <div key={p.pipeline_id} className="rounded-lg border p-4 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <span className="font-medium">{p.name}</span>
            <span className={`rounded-full px-2 py-0.5 text-xs ${p.status === "active" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>
              {p.status}
            </span>
          </div>
          <div className="mt-2 flex items-center gap-2 text-xs text-gray-400">
            <span>{p.sources.join(", ")}</span>
            <span>→</span>
            <span>{p.destinations.join(", ")}</span>
          </div>
          <div className="mt-2 flex gap-2">
            <button onClick={() => onToggle(p.pipeline_id)} className="text-xs text-blue-500">
              {p.status === "active" ? "Pause" : "Resume"}
            </button>
            <button onClick={() => onDelete(p.pipeline_id)} className="text-xs text-red-500">Delete</button>
          </div>
        </div>
      ))}
    </div>
  );
}
