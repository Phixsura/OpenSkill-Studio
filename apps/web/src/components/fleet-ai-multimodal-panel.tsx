"use client";
export function FleetAiMultimodalPanel({ pipelines, active, modalities, requests }: { pipelines: number; active: number; modalities: string[]; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎭 AI Multimodal</h3>
    <div className="text-sm">{active}/{pipelines} active · {modalities.join(", ")} · {requests.toLocaleString()} req/24h</div>
  </div>);
}
