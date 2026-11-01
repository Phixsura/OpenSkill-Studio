"use client";
export function FleetAiQuantV2Panel({ quantizers, active, models, bits, speedup, loss }: { quantizers: number; active: number; models: number; bits: number; speedup: number; loss: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 AI Quantizer v2</h3>
    <div className="text-sm">{active}/{quantizers} active · {models} models · {bits}-bit · {speedup}x speed · {loss}% loss</div>
  </div>);
}
