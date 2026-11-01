"use client";

interface Props { mttrSeconds: number; openIncidents: number; totalIncidents: number; appName: string; }

function fmtDuration(s: number) { return s < 60 ? `${s}s` : s < 3600 ? `${Math.round(s / 60)}m` : `${(s / 3600).toFixed(1)}h`; }

export default function APIDeveloperPlatformSDKApiDeveloperApiWebhookMTTRTrackerCard({ mttrSeconds, openIncidents, totalIncidents, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Webhook MTTR</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {openIncidents > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{openIncidents} open</span>}
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-blue-600">{fmtDuration(mttrSeconds)}</p>
          <p className="text-[9px] text-gray-400">MTTR</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-red-500">{openIncidents}</p>
          <p className="text-[9px] text-gray-400">Open</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{totalIncidents}</p>
          <p className="text-[9px] text-gray-400">Total</p>
        </div>
      </div>
    </div>
  );
}
