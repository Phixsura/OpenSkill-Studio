"use client";

interface Stage { stage: number; name: string; trafficPct: number; status: string; }
interface ProgDeliveryPanelProps { deployment: string; stages: Stage[];
  currentStage: number; status: string; }

const STAGE_COLORS: Record<string, string> = {
  completed: "bg-green-500 text-white", failed: "bg-red-500 text-white",
  pending: "bg-gray-200 dark:bg-gray-700 text-gray-500",
};

export function ProgDeliveryPanel({ deployment, stages, currentStage, status }: ProgDeliveryPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">🎯 Progressive: {deployment}</h3>
        <span className={`text-xs ${status === "complete" ? "text-green-600" : status === "rolled_back" ? "text-red-500" : "text-blue-500"}`}>
          {status === "complete" ? "✅ Complete" : status === "rolled_back" ? "⏪ Rolled Back" : `Stage ${currentStage + 1}`}
        </span>
      </div>
      <div className="flex items-center gap-1 p-4">
        {stages.map((s, i) => (
          <div key={s.stage} className="flex items-center flex-1">
            <div className={`flex-1 p-2 rounded text-center text-[10px] ${STAGE_COLORS[s.status] ?? STAGE_COLORS.pending}`}>
              <div className="font-medium">{s.name}</div>
              <div>{s.trafficPct}%</div>
            </div>
            {i < stages.length - 1 && <span className="text-gray-300 mx-0.5">→</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
