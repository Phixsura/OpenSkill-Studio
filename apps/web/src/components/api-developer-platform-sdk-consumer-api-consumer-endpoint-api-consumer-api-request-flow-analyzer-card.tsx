"use client";

interface Step { name: string; service: string; latencyMs: number; status: string; }
interface Flow { id: string; endpoint: string; totalMs: number; steps: Step[]; }
interface Analysis { totalFlows: number; avgMs: number; bottleneckService: string; bottleneckMs: number; slowestStep: string; errors: number; }
interface Props { analysis: Analysis; recentFlows: Flow[]; consumerId: string; appName: string; }

const statusColors: Record<string, string> = { ok: "bg-green-500", slow: "bg-amber-500", error: "bg-red-500" };

export default function APIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerApiRequestFlowAnalyzerCard({ analysis, recentFlows, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔬 Request Flow Analyzer</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {analysis.totalFlows} flows</p>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[10px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{analysis.avgMs}ms</div><div className="text-gray-400">Avg Latency</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-red-600">{analysis.bottleneckService || "—"}</div><div className="text-gray-400">Bottleneck</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{analysis.errors}</div><div className="text-gray-400">Errors</div></div>
      </div>
      {recentFlows.length > 0 && (
        <div className="space-y-2">
          {recentFlows.slice(0, 3).map((f) => (
            <div key={f.id} className="rounded bg-gray-50 p-1.5 dark:bg-gray-800">
              <div className="flex justify-between text-[10px]"><code className="text-gray-600">{f.endpoint}</code><span className="text-gray-400">{f.totalMs}ms</span></div>
              <div className="mt-0.5 flex gap-0.5">{f.steps.map((s, i) => <div key={i} className={`h-1.5 rounded ${statusColors[s.status] ?? "bg-gray-300"}`} style={{ flex: s.latencyMs }} title={`${s.name}: ${s.latencyMs}ms`} />)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
