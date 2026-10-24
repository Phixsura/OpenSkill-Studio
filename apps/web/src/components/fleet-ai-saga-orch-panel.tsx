"use client";
export function FleetAiSagaOrchPanel({ orchestrators, active, sagas, completed, compensated }: { orchestrators: number; active: number; sagas: number; completed: number; compensated: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 AI Saga Orchestrator</h3>
    <div className="text-sm">{active}/{orchestrators} active · {sagas.toLocaleString()} sagas · {completed.toLocaleString()} completed · {compensated} compensated</div>
  </div>);
}
