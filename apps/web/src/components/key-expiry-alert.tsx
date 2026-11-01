"use client";

interface ExpiringKey { name: string; daysUntilExpiry: number; status: string; urgency?: string; }
interface KeyExpiryAlertProps { expiring: ExpiringKey[]; expired: ExpiringKey[];
  message: string; needsAction: boolean; onRotate: (name: string) => void; }

export function KeyExpiryAlert({ expiring, expired, message, needsAction, onRotate }: KeyExpiryAlertProps) {
  if (!needsAction) return <p className="text-xs text-green-600">✅ All keys current</p>;
  return (
    <div className="rounded-xl border border-red-200 dark:border-red-800 p-4 bg-red-50 dark:bg-red-900/10">
      <p className="text-sm font-medium text-red-700 mb-2">{message}</p>
      <div className="space-y-1">
        {[...expired, ...expiring].map(k => (
          <div key={k.name} className="flex items-center justify-between text-sm">
            <div>
              <span className="font-mono text-xs">{k.name}</span>
              <span className={`text-xs ml-2 ${k.status === "expired" ? "text-red-600" : "text-yellow-600"}`}>
                {k.status === "expired" ? "Expired" : `${k.daysUntilExpiry}d left`}
              </span>
            </div>
            <button onClick={() => onRotate(k.name)}
              className="text-xs px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700">Rotate</button>
          </div>
        ))}
      </div>
    </div>
  );
}
