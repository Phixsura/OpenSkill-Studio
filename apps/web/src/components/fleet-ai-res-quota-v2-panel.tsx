"use client";
export function FleetAiResQuotaV2Panel({ quotas, active, namespaces, gpus, memoryGb }: { quotas: number; active: number; namespaces: number; gpus: number; memoryGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Resource Quota v2</h3>
    <div className="text-sm">{active}/{quotas} active · {namespaces} namespaces · {gpus} GPUs · {memoryGb}GB memory</div>
  </div>);
}
