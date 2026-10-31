"use client";

interface CanaryReleaseInfo {
  release_id: string;
  stable_version: string;
  canary_version: string;
  traffic_pct: number;
  status: "active" | "promoted" | "rolled_back";
  stable_error_rate: number;
  canary_error_rate: number;
  stable_latency_ms: number;
  canary_latency_ms: number;
}

interface CanaryReleaseCardProps {
  release: CanaryReleaseInfo;
  appName: string;
}

const STATUS_STYLES: Record<string, { label: string; bg: string; text: string }> = {
  active: {
    label: "Active",
    bg: "bg-blue-100 dark:bg-blue-900/30",
    text: "text-blue-700 dark:text-blue-400",
  },
  promoted: {
    label: "Promoted",
    bg: "bg-green-100 dark:bg-green-900/30",
    text: "text-green-700 dark:text-green-400",
  },
  rolled_back: {
    label: "Rolled Back",
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-700 dark:text-red-400",
  },
};

export default function CanaryReleaseCard({ release: r, appName }: CanaryReleaseCardProps) {
  const st = STATUS_STYLES[r.status] ?? STATUS_STYLES.active;
  const canaryWorse = r.canary_error_rate > r.stable_error_rate * 1.5;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Canary Release</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${st.bg} ${st.text}`}>
          {st.label}
        </span>
      </div>

      {/* Traffic split */}
      <div className="mb-3">
        <div className="mb-1 flex items-center justify-between text-[11px] text-gray-500">
          <span>Stable {r.stable_version}</span>
          <span>Canary {r.canary_version}</span>
        </div>
        <div className="flex h-3 overflow-hidden rounded-full">
          <div className="bg-blue-500" style={{ width: `${100 - r.traffic_pct}%` }} />
          <div className="bg-yellow-500" style={{ width: `${r.traffic_pct}%` }} />
        </div>
        <div className="mt-0.5 flex items-center justify-between text-[10px] text-gray-400">
          <span>{(100 - r.traffic_pct).toFixed(0)}%</span>
          <span>{r.traffic_pct.toFixed(0)}%</span>
        </div>
      </div>

      {/* Metrics comparison */}
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded bg-gray-50 px-3 py-2 text-center dark:bg-gray-800/50">
          <p className="text-[10px] text-gray-500">Stable</p>
          <p className="text-sm font-medium text-gray-800 dark:text-gray-200">
            {r.stable_error_rate.toFixed(1)}% err
          </p>
          <p className="text-[11px] text-gray-400">{r.stable_latency_ms.toFixed(0)}ms</p>
        </div>
        <div
          className={`rounded px-3 py-2 text-center ${canaryWorse ? "bg-red-50 dark:bg-red-950/20" : "bg-gray-50 dark:bg-gray-800/50"}`}
        >
          <p className="text-[10px] text-gray-500">Canary</p>
          <p
            className={`text-sm font-medium ${canaryWorse ? "text-red-600 dark:text-red-400" : "text-gray-800 dark:text-gray-200"}`}
          >
            {r.canary_error_rate.toFixed(1)}% err
          </p>
          <p className="text-[11px] text-gray-400">{r.canary_latency_ms.toFixed(0)}ms</p>
        </div>
      </div>
    </div>
  );
}
