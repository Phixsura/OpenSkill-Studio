"use client";
export function FleetTelemetryPipelineV9Panel({ exporters, sps }: { exporters: number; sps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 Telemetry Pipeline v9</h3>
    <div className="text-sm">{exporters} exporters · {sps.toLocaleString()} spans/s</div>
  </div>);
}
