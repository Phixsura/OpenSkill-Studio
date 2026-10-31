"use client";

interface Analysis { endpoint: string; samples: number; avgReqBytes: number; avgRespBytes: number; maxReqBytes: number; maxRespBytes: number; }
interface Props { analyses: Analysis[]; totalTransferGb: number; largestEndpoint: string; appName: string; }

const fmtBytes = (b: number) => b >= 1048576 ? `${(b / 1048576).toFixed(1)} MB` : b >= 1024 ? `${(b / 1024).toFixed(1)} KB` : `${b} B`;

export default function APIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiApiConsumerRequestSizeAnalyzerCard({ analyses, totalTransferGb, largestEndpoint, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📏 Request Size Analyzer</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {totalTransferGb} GB total · Largest: {largestEndpoint || "—"}</p>
      </div>
      {analyses.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No size data</p>
      ) : (
        <div className="space-y-2">
          {analyses.slice(0, 6).map((a) => (
            <div key={a.endpoint} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{a.endpoint}</code>
                <span className="text-[10px] text-gray-400">{a.samples} samples</span>
              </div>
              <div className="mt-0.5 grid grid-cols-2 gap-2 text-[10px] text-gray-400">
                <span>Req avg: {fmtBytes(a.avgReqBytes)}</span>
                <span>Resp avg: {fmtBytes(a.avgRespBytes)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
