"use client";
export function FleetFargatePanel({ totalTasks, running, cpuUnits, memoryMb }: { totalTasks: number; running: number; cpuUnits: number; memoryMb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐳 Fargate</h3>
    <div className="text-sm">{running}/{totalTasks} running · {cpuUnits} CPU · {memoryMb}MB</div>
  </div>);
}
