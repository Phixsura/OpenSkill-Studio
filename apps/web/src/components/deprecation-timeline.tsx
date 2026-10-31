"use client";

interface DeprecationTimelineProps {
  phase: "announced" | "deprecation" | "final_warning" | "sunset";
  daysRemaining: number;
  sunsetDate: string;
  alternativeAppName?: string;
}

export function DeprecationTimeline({ phase, daysRemaining, sunsetDate, alternativeAppName }: DeprecationTimelineProps) {
  const phases = ["announced", "deprecation", "final_warning", "sunset"];
  const currentIdx = phases.indexOf(phase);
  const colors: Record<string, string> = {
    announced: "text-blue-600", deprecation: "text-yellow-600",
    final_warning: "text-orange-600", sunset: "text-red-600",
  };

  return (
    <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-800 dark:bg-yellow-900/20">
      <div className="flex items-center gap-2">
        <span className="text-lg">⚠️</span>
        <h3 className={`font-semibold ${colors[phase]}`}>
          {phase === "sunset" ? "This app has been sunset" : `Deprecation: ${daysRemaining} days remaining`}
        </h3>
      </div>
      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Sunset date: {sunsetDate}</p>
      <div className="mt-3 flex gap-1">
        {phases.map((p, i) => (
          <div key={p} className={`h-2 flex-1 rounded ${i <= currentIdx ? "bg-orange-500" : "bg-gray-200 dark:bg-gray-700"}`} />
        ))}
      </div>
      <div className="mt-1 flex justify-between text-xs text-gray-400">
        <span>Announced</span><span>Sunset</span>
      </div>
      {alternativeAppName && (
        <p className="mt-3 text-sm">💡 Consider switching to <strong>{alternativeAppName}</strong></p>
      )}
    </div>
  );
}
