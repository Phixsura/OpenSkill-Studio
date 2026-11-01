"use client";
export function FleetFinetunePanel({ total, running, completed, failed, epochs }: { total: number; running: number; completed: number; failed: number; epochs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎯 Fine-tuning</h3>
    <div className="text-sm">{running}🔄 {completed}✅ {failed}❌ · {epochs} epochs</div>
  </div>);
}
