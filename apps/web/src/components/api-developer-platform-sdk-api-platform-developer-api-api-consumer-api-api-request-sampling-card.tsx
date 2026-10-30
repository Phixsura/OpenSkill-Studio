"use client";

interface Props { sampleCount: number; sampleRate: number; avgDuration: number; maxSamples: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSamplingCard({ sampleCount, sampleRate, avgDuration, maxSamples, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Request Sampling</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {(sampleRate * 100).toFixed(1)}% rate</p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{sampleCount.toLocaleString()}</div><div className="text-gray-400">Sampled</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{avgDuration}ms</div><div className="text-gray-400">Avg</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{maxSamples.toLocaleString()}</div><div className="text-gray-400">Max</div></div>
      </div>
    </div>
  );
}
