"use client";

interface KeyStatus { keyId: string; daysSinceRotation: number; daysUntilDue: number;
  due: boolean; urgency: string; }
interface KeyRotationDashboardProps { keys: KeyStatus[]; totalKeys: number;
  dueCount: number; onRotate: (keyId: string) => void; }

export function KeyRotationDashboard({ keys, totalKeys, dueCount, onRotate }: KeyRotationDashboardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔄 Key Rotation</h3>
        <div className="flex gap-3 text-xs">
          <span className="text-gray-400">{totalKeys} keys</span>
          {dueCount > 0 && <span className="text-red-500 font-medium">{dueCount} due</span>}
        </div>
      </div>
      <div className="space-y-2">
        {keys.map(k => (
          <div key={k.keyId} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <p className="text-sm font-mono font-medium">{k.keyId}</p>
              <p className="text-xs text-gray-400">
                Rotated {Math.round(k.daysSinceRotation)}d ago
                {!k.due && ` · ${Math.round(k.daysUntilDue)}d until due`}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-0.5 rounded-full ${
                k.urgency === "overdue" ? "bg-red-100 text-red-700" :
                k.urgency === "due" ? "bg-yellow-100 text-yellow-700" :
                "bg-green-100 text-green-700"
              }`}>{k.urgency}</span>
              {k.due && (
                <button onClick={() => onRotate(k.keyId)}
                  className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Rotate</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
