"use client";

interface CronFields { minute: string; hour: string; day_of_month: string; month: string; day_of_week: string; }
interface CronScheduleDisplayProps { expression: string; description: string; fields: CronFields; }

const fieldLabels = ["Minute", "Hour", "Day", "Month", "Weekday"];

export function CronScheduleDisplay({ expression, description, fields }: CronScheduleDisplayProps) {
  const fieldValues = [fields.minute, fields.hour, fields.day_of_month, fields.month, fields.day_of_week];
  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <div>
        <p className="text-sm font-medium">{description}</p>
        <p className="mt-0.5 font-mono text-xs text-gray-400">{expression}</p>
      </div>
      <div className="flex gap-2">
        {fieldLabels.map((label, i) => (
          <div key={label} className="flex-1 rounded bg-gray-50 p-2 text-center dark:bg-gray-800">
            <p className="font-mono text-lg font-bold">{fieldValues[i]}</p>
            <p className="text-[10px] text-gray-400">{label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
