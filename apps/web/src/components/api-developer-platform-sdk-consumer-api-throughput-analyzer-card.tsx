"use client";

import { useState } from "react";

interface ThroughputSample {
  endpointId: string;
  timestamp: string;
  requestsPerSecond: number;
  avgLatencyMs: number;
  errorCount: number;
}

interface ThroughputAnalysis {
  endpointId: string;
  sampleCount: number;
  peakRps: number;
  avgRps: number;
  avgLatencyMs: number;
  totalErrors: number;
  errorRate: number;
  capacityStatus: string;
}

const STATUS_COLORS: Record<string, string> = {
  healthy: "text-green-600 dark:text-green-400",
  stressed: "text-yellow-600 dark:text-yellow-400",
  overloaded: "text-red-600 dark:text-red-400",
  spiky: "text-orange-600 dark:text-orange-400",
};

export default function ThroughputAnalyzerCard() {
  const [analyses, setAnalyses] = useState<ThroughputAnalysis[]>([
    {
      endpointId: "ep-users",
      sampleCount: 24,
      peakRps: 1250,
      avgRps: 480,
      avgLatencyMs: 45,
      totalErrors: 12,
      errorRate: 0.001,
      capacityStatus: "healthy",
    },
    {
      endpointId: "ep-search",
      sampleCount: 18,
      peakRps: 890,
      avgRps: 320,
      avgLatencyMs: 310,
      totalErrors: 87,
      errorRate: 0.015,
      capacityStatus: "stressed",
    },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Throughput Analyzer
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Measure and forecast API throughput capacity
      </p>

      <div className="mt-4 space-y-3">
        {analyses.map((a) => (
          <div
            key={a.endpointId}
            className="rounded-lg border border-zinc-100 p-4 dark:border-zinc-700"
          >
            <div className="flex items-center justify-between">
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">
                {a.endpointId}
              </span>
              <span
                className={`text-xs font-medium uppercase ${STATUS_COLORS[a.capacityStatus] ?? "text-zinc-500"}`}
              >
                {a.capacityStatus}
              </span>
            </div>
            <div className="mt-2 grid grid-cols-3 gap-2 text-center text-xs">
              <div>
                <div className="text-zinc-500 dark:text-zinc-400">Peak RPS</div>
                <div className="font-semibold text-zinc-900 dark:text-zinc-100">
                  {a.peakRps.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-zinc-500 dark:text-zinc-400">Avg RPS</div>
                <div className="font-semibold text-zinc-900 dark:text-zinc-100">
                  {a.avgRps}
                </div>
              </div>
              <div>
                <div className="text-zinc-500 dark:text-zinc-400">Latency</div>
                <div className="font-semibold text-zinc-900 dark:text-zinc-100">
                  {a.avgLatencyMs}ms
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {analyses.length} endpoints monitored
      </div>
    </div>
  );
}
