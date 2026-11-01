"use client";

interface StoredEvent { id: string; eventType: string; originalStatus: number; originalAt: string; }
interface Replay { replayId: string; eventId: string; originalStatus: number; replayStatus: number; diffDetected: boolean; }
interface Props { storedEvents: StoredEvent[]; replays: Replay[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiWebhookEventReplayCard({ storedEvents, replays, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Event Replay</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {storedEvents.length} stored</p>
      </div>
      {storedEvents.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No stored events</p>
      ) : (
        <div className="mb-3 space-y-1">
          {storedEvents.slice(0, 5).map((e) => (
            <div key={e.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <span className="text-gray-700 dark:text-gray-300">{e.eventType}</span>
              <div className="flex gap-2 text-gray-400"><span>{e.originalStatus}</span><span>{e.originalAt}</span></div>
            </div>
          ))}
        </div>
      )}
      {replays.length > 0 && (
        <div>
          <div className="text-[10px] text-gray-400 mb-1">Replays:</div>
          {replays.slice(0, 3).map((r) => (
            <div key={r.replayId} className="flex justify-between text-[9px]">
              <span className="text-gray-500">{r.eventId}</span>
              <span className={r.diffDetected ? "text-amber-500" : "text-green-500"}>{r.originalStatus} → {r.replayStatus} {r.diffDetected ? "DIFF" : "OK"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
