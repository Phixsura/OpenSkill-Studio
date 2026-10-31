"use client";

interface SeverityClassifierProps { severity: string; matchedSymptoms: string[];
  responseTimeMin: number; escalate: boolean;
  distribution: Record<string, number>; totalIncidents: number; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-500 text-white", high: "bg-orange-500 text-white",
  medium: "bg-yellow-400", low: "bg-blue-400 text-white",
};

export function SeverityClassifier({ severity, matchedSymptoms, responseTimeMin, escalate, distribution, totalIncidents }: SeverityClassifierProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚨 Severity Classifier</h3>
        <div className="flex gap-2">
          <span className={`px-2 py-0.5 text-xs rounded ${SEV_COLORS[severity] ?? ""}`}>{severity}</span>
          {escalate && <span className="text-xs text-red-500">📟 Escalate</span>}
        </div>
      </div>
      <div className="p-3 text-xs">
        <div className="text-gray-400 mb-1">Response: {responseTimeMin}min · Symptoms: {matchedSymptoms.join(", ") || "none"}</div>
        <div className="flex gap-2 mt-2">
          {Object.entries(distribution).map(([sev, count]) => (
            <span key={sev} className={`px-1.5 py-0.5 text-[10px] rounded ${SEV_COLORS[sev] ?? "bg-gray-200"}`}>
              {sev}: {count}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
