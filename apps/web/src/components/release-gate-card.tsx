"use client";

interface GateCheckInfo {
  gate_id: string;
  name: string;
  required: boolean;
  status: "pending" | "passed" | "failed" | "skipped";
  message: string;
}

interface ReleaseGateCardProps {
  version: string;
  gates: GateCheckInfo[];
  approved: boolean;
  appName: string;
}

const GATE_ICONS: Record<string, { icon: string; color: string }> = {
  pending: { icon: "○", color: "text-gray-400" },
  passed: { icon: "✓", color: "text-green-600 dark:text-green-400" },
  failed: { icon: "✕", color: "text-red-600 dark:text-red-400" },
  skipped: { icon: "—", color: "text-gray-400" },
};

export default function ReleaseGateCard({
  version,
  gates,
  approved,
  appName,
}: ReleaseGateCardProps) {
  const passedCount = gates.filter((g) => g.status === "passed").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Release Gates</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · v{version}
          </p>
        </div>
        {approved ? (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            ✓ Approved
          </span>
        ) : (
          <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
            {passedCount}/{gates.length} passed
          </span>
        )}
      </div>

      <div className="space-y-1.5">
        {gates.map((g) => {
          const st = GATE_ICONS[g.status] ?? GATE_ICONS.pending;
          return (
            <div
              key={g.gate_id}
              className="flex items-center justify-between rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span className={`text-sm font-bold ${st.color}`}>{st.icon}</span>
                <span className="text-sm text-gray-800 dark:text-gray-200">{g.name}</span>
                {!g.required && <span className="text-[10px] text-gray-400">optional</span>}
              </div>
              {g.message && <span className="text-[11px] text-gray-400">{g.message}</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
