"use client";
export function FleetSidecarInjectorV9Panel({ namespaces, pods }: { namespaces: number; pods: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💉 Sidecar Injector v9</h3>
    <div className="text-sm">{namespaces} namespaces · {pods} pods injected</div>
  </div>);
}
