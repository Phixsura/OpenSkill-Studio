"use client";

interface NegInfo { consumer_id: string; preferred_format: string; negotiations: number; }
interface Props { negotiations: NegInfo[]; formatDistribution: Record<string, number>; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiationCard({ negotiations, formatDistribution, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🤝 Content Negotiation</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {negotiations.length} consumers</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(formatDistribution).map(([fmt, count]) => (
          <span key={fmt} className="rounded bg-blue-50 px-1.5 py-0.5 text-[9px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">{fmt.split("/")[1]}: {count}</span>
        ))}
      </div>
      {negotiations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No negotiations configured</p>
      ) : (
        <div className="space-y-1">
          {negotiations.slice(0, 5).map((n) => (
            <div key={n.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{n.consumer_id}</span>
              <span className="text-gray-400">{n.preferred_format.split("/")[1]} · {n.negotiations} negs</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
