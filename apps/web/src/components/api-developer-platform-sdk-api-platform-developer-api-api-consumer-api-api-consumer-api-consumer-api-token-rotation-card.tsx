"use client";

interface Token { id: string; createdAt: string; expiresAt: string; revoked: boolean; hasPredecessor: boolean; }
interface Props { tokens: Token[]; consumerId: string; gracePeriodHours: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiTokenRotationCard({ tokens, consumerId, gracePeriodHours, appName }: Props) {
  const active = tokens.filter((t) => !t.revoked).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Token Rotation</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · Grace: {gracePeriodHours}h</p>
      </div>
      <div className="mb-2 text-[11px] text-gray-500">{active} active / {tokens.length} total</div>
      {tokens.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tokens</p>
      ) : (
        <div className="space-y-1">
          {tokens.map((t) => (
            <div key={t.id} className={`flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800 ${t.revoked ? "opacity-50" : ""}`}>
              <div>
                <code className="text-gray-600 dark:text-gray-400">{t.id}</code>
                {t.hasPredecessor && <span className="ml-1 text-blue-400">↻</span>}
              </div>
              <div className="flex gap-2">
                <span className="text-gray-400">{t.expiresAt}</span>
                {t.revoked && <span className="text-red-400">revoked</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
