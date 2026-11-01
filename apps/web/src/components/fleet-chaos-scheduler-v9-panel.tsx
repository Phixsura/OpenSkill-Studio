"use client";
export function FleetChaosSchedulerV9Panel({ schedules, runs }: { schedules: number; runs: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌪️ Chaos Scheduler v9</h3>
    <div className="text-sm">{schedules} schedules · {runs} runs completed</div>
  </div>);
}
