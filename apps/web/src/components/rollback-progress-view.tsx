"use client";

interface Step { name: string; status: string; }
interface RollbackProgressViewProps { rollbackId: string; fromVersion: string; toVersion: string;
  reason: string; steps: Step[]; status: string; onCancel: () => void; }

const stepIcon = (s: string) => s === "completed" ? "✅" : s === "in_progress" ? "⏳" : s === "failed" ? "❌" : "⬜";

export function RollbackProgressView({ rollbackId, fromVersion, toVersion, reason, steps, status, onCancel }: RollbackProgressViewProps) {
  return (
    <div className="space-y-4 rounded-lg border border-orange-300 p-5 dark:border-orange-700">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-orange-600">Rolling Back</h2>
          <p className="text-sm text-gray-400">v{fromVersion} → v{toVersion}</p>
        </div>
        <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-medium text-orange-700 dark:bg-orange-900/30">
          {status}
        </span>
      </div>
      <p className="text-sm text-gray-500">Reason: {reason}</p>
      <div className="flex items-center justify-center gap-2">
        {steps.map((s, i) => (
          <div key={s.name} className="flex items-center gap-1">
            <div className="flex flex-col items-center">
              <span className="text-lg">{stepIcon(s.status)}</span>
              <span className="text-[10px] capitalize text-gray-400">{s.name.replace(/_/g, " ")}</span>
            </div>
            {i < steps.length - 1 && <span className="text-gray-300">→</span>}
          </div>
        ))}
      </div>
      {status === "pending" && (
        <button onClick={onCancel} className="w-full rounded border border-red-300 py-1.5 text-sm text-red-600">
          Cancel Rollback
        </button>
      )}
    </div>
  );
}
