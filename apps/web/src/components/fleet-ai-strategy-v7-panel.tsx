"use client";
export function FleetAiStrategyV7Panel({ planners, active, initiatives, completed, okrs, onTrack }: { planners: number; active: number; initiatives: number; completed: number; okrs: number; onTrack: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 AI Strategy v7</h3>
    <div className="text-sm">{active}/{planners} active · {initiatives} initiatives · {completed} done · {okrs} OKRs · {onTrack}% on track</div>
  </div>);
}
