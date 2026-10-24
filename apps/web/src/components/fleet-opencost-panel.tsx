"use client";
export function FleetOpencostPanel({ namespaces, dailyCost, idleCost, efficiency }: { namespaces: number; dailyCost: number; idleCost: number; efficiency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 OpenCost</h3>
    <div className="text-sm">${dailyCost}/day · ${idleCost} idle · {efficiency}% efficient</div>
  </div>);
}
