"use client";
export function FleetAiModelExpPanel({ exporters, active, exports, formats, sizeGb }: { exporters: number; active: number; exports: number; formats: number; sizeGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📤 AI Model Export</h3>
    <div className="text-sm">{active}/{exporters} active · {exports.toLocaleString()} exports · {formats} formats · {sizeGb}GB</div>
  </div>);
}
