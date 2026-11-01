"use client";

interface SecretStatus { secretName: string; ageDays: number; dueInDays: number;
  status: string; needsRotation: boolean; }
interface SecretRotationPanelProps { secrets: SecretStatus[]; onRotate: (name: string) => void; }

const STATUS_BADGE: Record<string, { bg: string; text: string }> = {
  ok: { bg: "bg-green-100 dark:bg-green-900/20", text: "text-green-700 dark:text-green-400" },
  warning: { bg: "bg-yellow-100 dark:bg-yellow-900/20", text: "text-yellow-700 dark:text-yellow-400" },
  overdue: { bg: "bg-red-100 dark:bg-red-900/20", text: "text-red-700 dark:text-red-400" },
};

export function SecretRotationPanel({ secrets, onRotate }: SecretRotationPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 Secret Rotation</h3>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {secrets.map(s => {
          const badge = STATUS_BADGE[s.status] ?? STATUS_BADGE.ok;
          return (
            <div key={s.secretName} className="flex items-center justify-between px-4 py-3">
              <div>
                <div className="text-sm font-mono">{s.secretName}</div>
                <div className="text-xs text-gray-400">{s.ageDays}d old · {s.dueInDays}d until rotation</div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 text-[10px] rounded-full ${badge.bg} ${badge.text}`}>{s.status}</span>
                {s.needsRotation && (
                  <button onClick={() => onRotate(s.secretName)}
                    className="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600">Rotate</button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
