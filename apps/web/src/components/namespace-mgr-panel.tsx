"use client";
interface Namespace { name: string; tenant: string; status: string; }
interface NamespaceMgrPanelProps { namespaces: Namespace[]; tenants: number; }
export function NamespaceMgrPanel({ namespaces, tenants }: NamespaceMgrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Namespaces</h3>
        <span className="text-xs text-gray-400">{namespaces.length} namespaces · {tenants} tenants</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {namespaces.map(ns => (
          <div key={ns.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{ns.name}</span>
            <span className="text-gray-400">{ns.tenant} · {ns.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
