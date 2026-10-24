"use client";
interface Resource { id: string; type: string; owner: string; version: number; status: string; }
interface ResLifecyclePanelProps { resources: Resource[]; total: number; auditEntries: number; }
export function ResLifecyclePanel({ resources, total, auditEntries }: ResLifecyclePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">♻️ Resource Lifecycle</h3>
        <span className="text-xs text-gray-400">{total} resources · {auditEntries} audit entries</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {resources.map(r => (
          <div key={r.id} className="flex justify-between px-4 py-1.5 text-xs">
            <div><span className="font-mono">{r.id}</span> <span className="text-gray-400">({r.type})</span></div>
            <span className="text-gray-400">v{r.version} · {r.owner} · {r.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
