"use client";

interface Context { id: string; traceId: string; spanId: string; parentSpanId: string | null; attributes: Record<string, string>; baggageCount: number; }
interface Props { contexts: Context[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestContextCard({ contexts, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Request Context</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {contexts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No active contexts</p>
      ) : (
        <div className="space-y-2">
          {contexts.slice(0, 5).map((c) => (
            <div key={c.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[10px]">
                <code className="text-blue-600 dark:text-blue-400">{c.traceId.slice(0, 16)}...</code>
                <span className="text-gray-400">{c.baggageCount} baggage</span>
              </div>
              <div className="mt-0.5 text-[9px] text-gray-400">
                span: {c.spanId}{c.parentSpanId && ` ← ${c.parentSpanId}`}
              </div>
              {Object.keys(c.attributes).length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {Object.entries(c.attributes).slice(0, 4).map(([k, v]) => (
                    <span key={k} className="rounded bg-gray-200 px-1 py-0.5 text-[8px] text-gray-600 dark:bg-gray-700 dark:text-gray-400">{k}={v}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
