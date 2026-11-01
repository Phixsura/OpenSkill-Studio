"use client";

interface PinInfo { consumer_id: string; pinned_version: string; reason: string; auto_upgrade: boolean; }
interface Props { pins: PinInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiVersionPinningCard({ pins, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📌 Version Pinning</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {pins.length} pinned</p>
      </div>
      {pins.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No version pins</p>
      ) : (
        <div className="space-y-1">
          {pins.map((p) => (
            <div key={p.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.consumer_id}</span>
              <div className="flex items-center gap-1">
                <span className="rounded bg-purple-100 px-1 text-[9px] text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">{p.pinned_version}</span>
                {p.auto_upgrade && <span className="text-[9px] text-green-600">↑auto</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
