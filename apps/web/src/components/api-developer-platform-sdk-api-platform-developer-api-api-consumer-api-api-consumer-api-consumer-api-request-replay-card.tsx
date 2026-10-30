"use client";

interface Replay { id: string; originalId: string; originalStatus: number; replayStatus: number; diffDetected: boolean; replayedAt: string; }
interface Props { replays: Replay[]; storedCount: number; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestReplayCard({ replays, storedCount, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Request Replay</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {storedCount} stored requests</p>
      </div>
      {replays.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No replays yet</p>
      ) : (
        <div className="space-y-1">
          {replays.slice(0, 6).map((r) => (
            <div key={r.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <span className="text-gray-600 dark:text-gray-400">{r.originalId}</span>
              <div className="flex gap-2">
                <span className="text-gray-500">{r.originalStatus} → {r.replayStatus}</span>
                <span className={r.diffDetected ? "text-amber-500" : "text-green-500"}>{r.diffDetected ? "DIFF" : "OK"}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
