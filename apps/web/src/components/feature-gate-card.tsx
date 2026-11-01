"use client";

interface GateInfo {
  gate_id: string;
  name: string;
  condition_count: number;
  match_all: boolean;
  eval_count: number;
  pass_rate: number;
}

interface FeatureGateCardProps {
  gates: GateInfo[];
  appName: string;
}

export default function FeatureGateCard({ gates, appName }: FeatureGateCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Feature Gates</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{gates.length} gates</span>
      </div>

      {gates.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No feature gates</p>
      ) : (
        <div className="space-y-2">
          {gates.map((g) => (
            <div
              key={g.gate_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-800 dark:text-gray-200">{g.name}</span>
                  <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">
                    {g.condition_count} conditions · {g.match_all ? "AND" : "OR"}
                  </span>
                </div>
                <span
                  className={`text-xs font-medium ${g.pass_rate >= 50 ? "text-green-600 dark:text-green-400" : "text-yellow-600 dark:text-yellow-400"}`}
                >
                  {g.pass_rate}% pass
                </span>
              </div>
              <p className="mt-0.5 text-[11px] text-gray-400">{g.eval_count} evaluations</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
