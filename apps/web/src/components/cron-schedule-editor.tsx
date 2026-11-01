"use client";

interface CronScheduleEditorProps { expression: string; description: string;
  fields: Record<string, string>; valid: boolean; onChange: (expr: string) => void; }

const PRESETS = [
  { label: "Every minute", value: "* * * * *" },
  { label: "Hourly", value: "0 * * * *" },
  { label: "Daily midnight", value: "0 0 * * *" },
  { label: "Weekly", value: "0 0 * * 0" },
  { label: "Monthly", value: "0 0 1 * *" },
];

export function CronScheduleEditor({ expression, description, fields, valid, onChange }: CronScheduleEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏰ Cron Schedule</h3>
      </div>
      <div className="p-4 space-y-3">
        <input value={expression} onChange={e => onChange(e.target.value)}
          className="w-full px-3 py-2 text-sm font-mono border rounded-lg dark:bg-gray-800 dark:border-gray-600" />
        <div className={`text-xs ${valid ? "text-green-600" : "text-red-500"}`}>{description}</div>
        {valid && (
          <div className="flex gap-2 flex-wrap">
            {Object.entries(fields).map(([k, v]) => (
              <span key={k} className="px-2 py-0.5 text-[10px] bg-gray-100 dark:bg-gray-800 rounded">
                {k.replaceAll("_", " ")}: <span className="font-mono font-bold">{v}</span>
              </span>
            ))}
          </div>
        )}
        <div className="flex gap-1 flex-wrap">
          {PRESETS.map(p => (
            <button key={p.value} onClick={() => onChange(p.value)}
              className="px-2 py-0.5 text-[10px] bg-blue-50 text-blue-600 dark:bg-blue-900/20 rounded hover:bg-blue-100">{p.label}</button>
          ))}
        </div>
      </div>
    </div>
  );
}
