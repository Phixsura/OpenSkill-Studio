"use client";
export function FleetKubeflowPanel({ clusters, healthy, pipelines, notebooks, experiments }: { clusters: number; healthy: number; pipelines: number; notebooks: number; experiments: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔬 Kubeflow</h3>
    <div className="text-sm">{healthy}/{clusters} healthy · {pipelines} pipelines · {notebooks} notebooks · {experiments} exps</div>
  </div>);
}
