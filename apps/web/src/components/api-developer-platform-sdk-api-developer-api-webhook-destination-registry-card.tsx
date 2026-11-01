"use client";

interface DestInfo { destination_id: string; url: string; name: string; active: boolean; total_deliveries: number; subscribed_events: string[]; }
interface Props { destinations: DestInfo[]; activeCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperApiWebhookDestinationRegistryCard({ destinations, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Destination Registry</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount}/{destinations.length} active</p>
      </div>
      {destinations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No destinations</p>
      ) : (
        <div className="space-y-2">
          {destinations.slice(0, 5).map((d) => (
            <div key={d.destination_id} className={`rounded-lg px-3 py-2 ${d.active ? "bg-gray-50 dark:bg-gray-800" : "bg-gray-100 opacity-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{d.name}</span>
                <span className="text-gray-400">{d.total_deliveries.toLocaleString()} deliveries</span>
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {d.subscribed_events.slice(0, 4).map((e) => (
                  <span key={e} className="rounded bg-blue-50 px-1 py-0.5 text-[9px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">{e}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
