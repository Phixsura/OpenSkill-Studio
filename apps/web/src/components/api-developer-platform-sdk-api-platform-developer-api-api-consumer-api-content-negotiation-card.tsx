"use client";

interface PrefInfo { consumer_id: string; preferred_format: string; accepted_formats: string[]; compression: string; }
interface Props { preferences: PrefInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiContentNegotiationCard({ preferences, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📄 Content Negotiation</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {preferences.length} consumers</p>
      </div>
      {preferences.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No preferences set</p>
      ) : (
        <div className="space-y-1.5">
          {preferences.map((p) => (
            <div key={p.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
                <span className="font-medium text-blue-600 dark:text-blue-400">{p.preferred_format}</span>
              </div>
              <div className="flex gap-1 mt-0.5">
                {p.accepted_formats.map((f) => <span key={f} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{f}</span>)}
                {p.compression !== "none" && <span className="rounded bg-green-100 px-1 text-[9px] text-green-700 dark:bg-green-900/30 dark:text-green-400">{p.compression}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
