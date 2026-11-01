"use client";

interface EnvStage { environment: string; status: string; requiresApproval: boolean; }
interface PromotionPipelineProps { version: string; pipeline: EnvStage[];
  currentEnv: string; onPromote: (env: string) => void; }

const ENV_COLORS: Record<string, string> = {
  deployed: "bg-green-500 text-white", pending: "bg-gray-200 dark:bg-gray-700 text-gray-500",
  promoting: "bg-blue-500 text-white",
};

export function PromotionPipeline({ version, pipeline, currentEnv, onPromote }: PromotionPipelineProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Promotion: v{version}</h3>
        <span className="text-xs text-gray-400">current: {currentEnv}</span>
      </div>
      <div className="flex items-center gap-1 p-4">
        {pipeline.map((s, i) => (
          <div key={s.environment} className="flex items-center flex-1">
            <div className={`flex-1 rounded-lg p-3 text-center ${ENV_COLORS[s.status] ?? ENV_COLORS.pending}`}>
              <div className="text-xs font-medium capitalize">{s.environment}</div>
              <div className="text-[10px]">{s.status}</div>
              {s.status === "pending" && (
                <button onClick={() => onPromote(s.environment)}
                  className="mt-1 px-2 py-0.5 text-[10px] bg-blue-600 text-white rounded">
                  {s.requiresApproval ? "🔐 Approve" : "Promote"}
                </button>
              )}
            </div>
            {i < pipeline.length - 1 && <span className="text-gray-300 mx-1">→</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
