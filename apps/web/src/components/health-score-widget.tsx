"use client";

interface Signal { raw: number; normalized: number; weighted: number; weight: number; }
interface HealthScoreWidgetProps { score: number; grade: string; status: string;
  signals: Record<string, Signal>; }

const gradeColor: Record<string, string> = {
  A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-orange-600", F: "text-red-600",
};
const signalLabels: Record<string, string> = {
  uptime: "Uptime", error_rate: "Error Rate", latency: "Latency",
  crash_free: "Crash-Free", user_satisfaction: "User Satisfaction",
};

export function HealthScoreWidget({ score, grade, status, signals }: HealthScoreWidgetProps) {
  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <div className="text-center">
        <span className={`text-5xl font-black ${gradeColor[grade] ?? ""}`}>{grade}</span>
        <p className="mt-1 text-2xl font-bold">{score}/100</p>
        <p className={`text-sm ${status === "healthy" ? "text-green-500" : status === "degraded" ? "text-yellow-500" : "text-red-500"}`}>
          {status}
        </p>
      </div>
      <div className="space-y-2">
        {Object.entries(signals).map(([key, s]) => (
          <div key={key}>
            <div className="flex justify-between text-xs">
              <span>{signalLabels[key] ?? key}</span>
              <span className="text-gray-400">{s.weighted}/{s.weight}</span>
            </div>
            <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className="h-full rounded-full bg-blue-500"
                style={{ width: `${s.normalized}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
