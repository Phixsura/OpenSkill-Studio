"use client";

interface ResourceDataPoint {
  timestamp: string;
  cpu: number;
  memory: number;
  network: number;
}

export function ExtensionResourceGraph({
  data,
  extensionName,
  cpuLimit,
  memoryLimit,
}: {
  data: ResourceDataPoint[];
  extensionName: string;
  cpuLimit: number;
  memoryLimit: number;
}) {
  const maxCpu = Math.max(cpuLimit, ...data.map((d) => d.cpu));
  const maxMem = Math.max(memoryLimit, ...data.map((d) => d.memory));
  const latestCpu = data.length > 0 ? data[data.length - 1].cpu : 0;
  const latestMem = data.length > 0 ? data[data.length - 1].memory : 0;
  const latestNet = data.length > 0 ? data[data.length - 1].network : 0;

  const cpuPercent = Math.round((latestCpu / cpuLimit) * 100);
  const memPercent = Math.round((latestMem / memoryLimit) * 100);

  return (
    <div className="rounded-xl border dark:border-gray-700 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📈 {extensionName} Resources</h2>
        <div className="flex gap-4 text-xs text-gray-500">
          <span>CPU: <span className={cpuPercent > 90 ? "text-red-500 font-bold" : cpuPercent > 70 ? "text-yellow-500" : "text-green-500"}>{cpuPercent}%</span></span>
          <span>Mem: <span className={memPercent > 90 ? "text-red-500 font-bold" : memPercent > 70 ? "text-yellow-500" : "text-green-500"}>{memPercent}%</span></span>
          <span>Net: {latestNet} KB/s</span>
        </div>
      </div>

      {/* Sparkline bars */}
      <div className="space-y-3">
        <ResourceBar label="CPU" values={data.map((d) => d.cpu)} max={maxCpu} limit={cpuLimit} unit="%" color="blue" />
        <ResourceBar label="Memory" values={data.map((d) => d.memory)} max={maxMem} limit={memoryLimit} unit="MB" color="purple" />
      </div>

      {/* Timeline labels */}
      {data.length > 0 && (
        <div className="flex justify-between text-xs text-gray-400">
          <span>{data[0].timestamp}</span>
          <span>{data[data.length - 1].timestamp}</span>
        </div>
      )}
    </div>
  );
}

function ResourceBar({ label, values, max, limit, unit, color }: {
  label: string; values: number[]; max: number; limit: number; unit: string; color: string;
}) {
  const colorClasses: Record<string, string> = { blue: "bg-blue-500", purple: "bg-purple-500", green: "bg-green-500" };
  const latest = values.length > 0 ? values[values.length - 1] : 0;
  const limitPercent = Math.round((limit / max) * 100);

  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-500">{label}</span>
        <span className="font-mono">{latest}{unit} / {limit}{unit}</span>
      </div>
      <div className="relative w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
        {/* Limit marker */}
        <div className="absolute top-0 bottom-0 border-r-2 border-red-400 border-dashed" style={{ left: `${Math.min(100, limitPercent)}%` }} />
        {/* Sparkline */}
        <div className="flex h-full rounded-full overflow-hidden">
          {values.slice(-30).map((v, i) => (
            <div key={i} className="flex-1 flex items-end">
              <div className={`w-full ${v > limit ? "bg-red-500" : colorClasses[color]}`}
                style={{ height: `${Math.min(100, (v / max) * 100)}%`, minHeight: "1px" }} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
