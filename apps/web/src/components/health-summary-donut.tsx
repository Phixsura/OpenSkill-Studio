"use client";

interface HealthSummaryDonutProps { overallScore: number; status: string;
  signals: Record<string, number>; }

const statusStyle: Record<string, { color: string; emoji: string }> = {
  excellent: { color: "text-green-600", emoji: "🟢" },
  good: { color: "text-blue-600", emoji: "🔵" },
  fair: { color: "text-yellow-600", emoji: "🟡" },
  poor: { color: "text-red-600", emoji: "🔴" },
};

const signalLabels: Record<string, string> = {
  uptime: "Uptime", errors: "Error Rate", latency: "Latency",
  stability: "Stability", satisfaction: "Satisfaction",
};

export function HealthSummaryDonut({ overallScore, status, signals }: HealthSummaryDonutProps) {
  const s = statusStyle[status] ?? statusStyle.good;
  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <div className="text-center">
        <span className="text-3xl">{s.emoji}</span>
        <p className={`text-4xl font-black ${s.color}`}>{overallScore}</p>
        <p className="text-sm capitalize text-gray-400">{status}</p>
      </div>
      <div className="space-y-2">
        {Object.entries(signals).map(([key, val]) => (
          <div key={key}>
            <div className="flex justify-between text-xs">
              <span>{signalLabels[key] ?? key}</span>
              <span className="text-gray-400">{val}/100</span>
            </div>
            <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${val >= 90 ? "bg-green-500" : val >= 70 ? "bg-blue-500" : val >= 50 ? "bg-yellow-500" : "bg-red-500"}`}
                style={{ width: `${val}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
