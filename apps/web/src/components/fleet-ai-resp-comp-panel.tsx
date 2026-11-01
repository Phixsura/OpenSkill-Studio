"use client";
export function FleetAiRespCompPanel({ compressors, active, responses, ratio, savedGb }: { compressors: number; active: number; responses: number; ratio: number; savedGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗜️ AI Response Compressor</h3>
    <div className="text-sm">{active}/{compressors} active · {responses.toLocaleString()} resp · {ratio}x ratio · {savedGb}GB saved</div>
  </div>);
}
