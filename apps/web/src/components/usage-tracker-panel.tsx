"use client";

interface UsagePeaks {
  cpu: number;
  memoryMb: number;
  networkBytes: number;
  apiCalls: number;
}

interface UsageAverages {
  cpu: number;
  memoryMb: number;
  apiCalls: number;
}

interface UsageForecast {
  forecast: number;
  confidence: "low" | "medium" | "high";
}

const confColors: Record<string, string> = {
  low: "text-gray-500", medium: "text-yellow-600", high: "text-green-600",
};

function formatBytes(b: number) {
  if (b < 1024) return `${b}B`;
  if (b < 1048576) return `${(b / 1024).toFixed(1)}KB`;
  return `${(b / 1048576).toFixed(1)}MB`;
}

export function UsageTrackerPanel({
  peaks,
  averages,
  forecast,
  totalApiCalls,
  totalNetworkBytes,
  windowMinutes,
}: {
  peaks: UsagePeaks;
  averages: UsageAverages;
  forecast: UsageForecast;
  totalApiCalls: number;
  totalNetworkBytes: number;
  windowMinutes: number;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📈 Usage Tracker</h2>
        <span className="text-sm text-gray-500">Last {windowMinutes}min</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block mb-2">Peak Values</span>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">CPU</span><span className={`font-bold ${peaks.cpu > 80 ? "text-red-600" : ""}`}>{peaks.cpu}%</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Memory</span><span className="font-bold">{peaks.memoryMb}MB</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Network</span><span className="font-bold">{formatBytes(peaks.networkBytes)}</span></div>
            <div className="flex justify-between"><span className="text-gray-500">API Calls</span><span className="font-bold">{peaks.apiCalls}</span></div>
          </div>
        </div>

        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block mb-2">Averages</span>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between"><span className="text-gray-500">CPU</span><span className="font-bold">{averages.cpu}%</span></div>
            <div className="flex justify-between"><span className="text-gray-500">Memory</span><span className="font-bold">{averages.memoryMb}MB</span></div>
            <div className="flex justify-between"><span className="text-gray-500">API Calls/min</span><span className="font-bold">{averages.apiCalls}</span></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Total API Calls</span>
          <span className="font-bold">{totalApiCalls.toLocaleString()}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Total Network</span>
          <span className="font-bold">{formatBytes(totalNetworkBytes)}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Forecast (1h)</span>
          <div>
            <span className="font-bold">{forecast.forecast}</span>
            <span className={`text-xs ml-1 ${confColors[forecast.confidence]}`}>{forecast.confidence}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
