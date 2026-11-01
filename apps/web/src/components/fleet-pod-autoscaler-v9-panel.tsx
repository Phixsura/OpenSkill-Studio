"use client";
export function FleetPodAutoscalerV9Panel({ autoscalers, events }: { autoscalers: number; events: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Pod Autoscaler v9</h3>
    <div className="text-sm">{autoscalers} autoscalers · {events} events today</div>
  </div>);
}
