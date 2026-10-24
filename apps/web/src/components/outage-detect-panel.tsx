"use client";

interface OutageDetectPanelProps { outage: boolean; classification: string;
  affectedServices: string[]; downCount: number; degradedCount: number; }

const CLASS_STYLE: Record<string, string> = {
  major: "bg-red-500 text-white", partial: "bg-orange-500 text-white",
  degraded: "bg-yellow-500", none: "bg-green-500 text-white",
};

export function OutageDetectPanel({ outage, classification, affectedServices, downCount, degradedCount }: OutageDetectPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-center ${CLASS_STYLE[classification] ?? "bg-gray-500 text-white"}`}>
        <h3 className="font-bold text-lg">{outage ? `⚠ ${classification.toUpperCase()} OUTAGE` : "✅ All Systems Operational"}</h3>
        {outage && <p className="text-sm opacity-80">{downCount} down · {degradedCount} degraded</p>}
      </div>
      {affectedServices.length > 0 && (
        <div className="p-4">
          <div className="text-xs text-gray-400 mb-1">Affected Services</div>
          <div className="flex flex-wrap gap-1">
            {affectedServices.map(s => (
              <span key={s} className="text-xs px-2 py-0.5 rounded bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300">{s}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
