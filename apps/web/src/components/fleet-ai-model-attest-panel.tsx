"use client";
export function FleetAiModelAttestPanel({ attestors, active, models, signatures, verifications }: { attestors: number; active: number; models: number; signatures: number; verifications: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔏 AI Model Attestation</h3>
    <div className="text-sm">{active}/{attestors} active · {models} models · {signatures} signatures · {verifications.toLocaleString()} verifications</div>
  </div>);
}
