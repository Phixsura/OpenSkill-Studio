"use client";
export function FleetAiFutureV8Panel({ planners, active, capabilities, research, prototypes }: { planners: number; active: number; capabilities: number; research: number; prototypes: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔮 AI Future v8</h3>
    <div className="text-sm">{active}/{planners} active · {capabilities} capabilities · {research} research · {prototypes} prototypes</div>
  </div>);
}
