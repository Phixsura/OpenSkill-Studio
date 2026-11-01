"use client";

interface DevMetricsCardProps { appCount: number; installsDisplay: string;
  ratingDisplay: string; apiDisplay: string; supportGrade: string;
  qualityScore: number; avgResponseHours: number; }

const GRADE_COLOR: Record<string, string> = {
  A: "text-green-600", B: "text-yellow-600", C: "text-red-500",
};

export function DevMetricsCard({ appCount, installsDisplay, ratingDisplay,
  apiDisplay, supportGrade, qualityScore, avgResponseHours }: DevMetricsCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">📊 Developer Metrics</h3>
      <div className="grid grid-cols-3 gap-3 text-center mb-3">
        <div><p className="text-lg font-bold">{appCount}</p><p className="text-xs text-gray-400">Apps</p></div>
        <div><p className="text-lg font-bold">{installsDisplay}</p><p className="text-xs text-gray-400">Installs</p></div>
        <div><p className="text-lg font-bold">{ratingDisplay}</p><p className="text-xs text-gray-400">Rating</p></div>
      </div>
      <div className="flex justify-between text-sm mb-2">
        <span>API Calls: <strong>{apiDisplay}</strong></span>
        <span>Quality: <strong>{qualityScore}/100</strong></span>
      </div>
      <div className="flex justify-between text-sm">
        <span>Support Grade: <strong className={GRADE_COLOR[supportGrade] || ""}>{supportGrade}</strong></span>
        <span className="text-xs text-gray-400">Avg response: {avgResponseHours}h</span>
      </div>
    </div>
  );
}
