"use client";

interface RotationInfo {
  rotation_id: string;
  in_grace_period: boolean;
  completed: boolean;
}

interface WebhookSecretRotationCardProps {
  rotations: RotationInfo[];
  hasSecret: boolean;
  appName: string;
}

export default function WebhookSecretRotationCard({ rotations, hasSecret, appName }: WebhookSecretRotationCardProps) {
  const inGrace = rotations.filter((r) => r.in_grace_period).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Secret Rotation</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[11px] font-medium ${hasSecret ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>
          {hasSecret ? "Active" : "Not set"}
        </span>
      </div>

      {inGrace > 0 && (
        <div className="mb-3 rounded-lg bg-yellow-50 px-3 py-1.5 text-xs text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300">
          {inGrace} rotation in grace period
        </div>
      )}

      {rotations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rotations</p>
      ) : (
        <div className="space-y-1">
          {rotations.map((r) => (
            <div key={r.rotation_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-600 dark:text-gray-400">{r.rotation_id}</span>
              <span className="text-gray-400">{r.completed ? "completed" : r.in_grace_period ? "grace period" : "pending"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
