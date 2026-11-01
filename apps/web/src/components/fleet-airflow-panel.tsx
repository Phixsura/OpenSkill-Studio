"use client";
export function FleetAirflowPanel({ environments, healthy, dags, activeRuns, failed }: { environments: number; healthy: number; dags: number; activeRuns: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌊 Airflow</h3>
    <div className="text-sm">{healthy}/{environments} healthy · {dags} DAGs · {activeRuns} running</div>
    {failed > 0 && <span className="text-xs text-red-500">❌ {failed} failed/24h</span>}
  </div>);
}
