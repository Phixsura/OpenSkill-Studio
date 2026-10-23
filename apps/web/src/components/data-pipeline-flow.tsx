"use client";

interface Transform { step: number; type: string; }
interface DataPipelineFlowProps { name: string; sourceType: string; destinationType: string;
  transforms: Transform[]; status: string; schedule: string | null;
  onRun: () => void; onPause: () => void; }

const nodeIcon: Record<string, string> = {
  postgres: "🐘", mysql: "🐬", bigquery: "📊", s3: "📦", kafka: "📨",
  filter: "🔍", map: "🔄", aggregate: "📈", join: "🔗",
};

export function DataPipelineFlow({ name, sourceType, destinationType, transforms, status, schedule, onRun, onPause }: DataPipelineFlowProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">{name}</h2>
          {schedule && <p className="font-mono text-xs text-gray-400">{schedule}</p>}
        </div>
        <span className={`rounded-full px-2.5 py-0.5 text-xs ${status === "active" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>
          {status}
        </span>
      </div>
      <div className="flex items-center justify-center gap-2">
        <div className="rounded-lg border-2 border-blue-400 px-3 py-2 text-center">
          <span>{nodeIcon[sourceType] ?? "📄"}</span>
          <p className="text-xs capitalize">{sourceType}</p>
        </div>
        <span className="text-gray-300">→</span>
        {transforms.map(t => (
          <div key={t.step} className="flex items-center gap-2">
            <div className="rounded border px-2 py-1 text-center dark:border-gray-600">
              <span className="text-sm">{nodeIcon[t.type] ?? "⚙️"}</span>
              <p className="text-[10px] capitalize">{t.type}</p>
            </div>
            <span className="text-gray-300">→</span>
          </div>
        ))}
        <div className="rounded-lg border-2 border-green-400 px-3 py-2 text-center">
          <span>{nodeIcon[destinationType] ?? "📥"}</span>
          <p className="text-xs capitalize">{destinationType}</p>
        </div>
      </div>
      <div className="flex gap-2">
        <button onClick={onRun} className="flex-1 rounded bg-blue-600 py-1.5 text-sm text-white">Run Now</button>
        <button onClick={onPause} className="rounded border px-4 py-1.5 text-sm dark:border-gray-600">
          {status === "active" ? "Pause" : "Resume"}
        </button>
      </div>
    </div>
  );
}
