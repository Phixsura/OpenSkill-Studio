"use client";

interface AnomalyDetectionCardProps {
  metricName: string; currentValue: number; mean: number; upper: number; lower: number;
  isAnomaly: boolean; direction: string; severity: string;
}

export function AnomalyDetectionCard({ metricName, currentValue, mean, upper, lower, isAnomaly, direction, severity }: AnomalyDetectionCardProps) {
  const sevColors: Record<string, string> = { critical: "border-red-500 bg-red-50", warning: "border-yellow-500 bg-yellow-50", info: "border-gray-200" };
  return (
    <div className={`rounded-lg border p-4 dark:border-gray-700 ${isAnomaly ? sevColors[severity] || "" : ""}`}>
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{metricName}</h3>
        {isAnomaly && <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${severity === "critical" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"}`}>
          {severity} — {direction}
        </span>}
      </div>
      <p className={`mt-2 text-3xl font-bold text-center ${isAnomaly ? "text-red-600" : ""}`}>{currentValue}</p>
      <div className="mt-2 flex justify-between text-xs text-gray-400">
        <span>Lower: {lower}</span>
        <span>Mean: {mean}</span>
        <span>Upper: {upper}</span>
      </div>
    </div>
  );
}
