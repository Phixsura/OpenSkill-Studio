"use client";

interface KeyRotationStatusProps { dueKeys: string[]; upcomingKeys: string[];
  actionNeeded: boolean; onRotate: (key: string) => void; }

export function KeyRotationStatus({ dueKeys, upcomingKeys, actionNeeded, onRotate }: KeyRotationStatusProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Key Rotation</h3>
        {actionNeeded && <span className="text-xs text-red-500 font-medium">⚠ {dueKeys.length} overdue</span>}
      </div>
      {dueKeys.length > 0 && (
        <div className="border-b dark:border-gray-700 bg-red-50 dark:bg-red-900/10 p-3">
          <div className="text-xs text-red-700 mb-1">Rotation Overdue</div>
          {dueKeys.map(k => (
            <div key={k} className="flex items-center justify-between py-0.5">
              <span className="text-xs font-mono">{k}</span>
              <button onClick={() => onRotate(k)} className="px-2 py-0.5 text-xs bg-red-500 text-white rounded">Rotate Now</button>
            </div>
          ))}
        </div>
      )}
      {upcomingKeys.length > 0 && (
        <div className="p-3">
          <div className="text-xs text-yellow-600 mb-1">Upcoming (within 7 days)</div>
          {upcomingKeys.map(k => (
            <div key={k} className="text-xs font-mono text-gray-400 py-0.5">{k}</div>
          ))}
        </div>
      )}
      {dueKeys.length === 0 && upcomingKeys.length === 0 && (
        <div className="p-4 text-center text-sm text-gray-400">✅ All keys current</div>
      )}
    </div>
  );
}
