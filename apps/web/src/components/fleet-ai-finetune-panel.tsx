"use client";
export function FleetAiFinetunPanel({ jobs, running, completed, failed, epochs }: { jobs: number; running: number; completed: number; failed: number; epochs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 AI Fine-Tuning</h3>
    <div className="text-sm">{running} running · {completed} done · {failed} failed · {epochs} epochs</div>
  </div>);
}
