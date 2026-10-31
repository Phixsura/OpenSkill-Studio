"use client";
import { useState } from "react";

interface PlanComparison { plan: string; totalCents: number; overageItems: number; }

const metrics = [
  { key: "api_calls", label: "API Calls (K)", default: 50 },
  { key: "compute", label: "Compute (hours)", default: 10 },
  { key: "storage", label: "Storage (GB)", default: 5 },
  { key: "bandwidth", label: "Bandwidth (GB)", default: 10 },
];

export function CostCalculatorWidget({ plans, onCalculate }: {
  plans: PlanComparison[]; onCalculate?: (usage: Record<string, number>) => void;
}) {
  const [usage, setUsage] = useState<Record<string, number>>(
    Object.fromEntries(metrics.map(m => [m.key, m.default]))
  );

  return (
    <div className="space-y-4">
      <h3 className="font-bold text-sm">Cost Calculator</h3>
      <div className="grid grid-cols-2 gap-2">
        {metrics.map(m => (
          <div key={m.key}>
            <label className="text-xs text-gray-500 block mb-0.5">{m.label}</label>
            <input type="number" value={usage[m.key]} onChange={e => setUsage({ ...usage, [m.key]: Number(e.target.value) })}
              className="w-full border dark:border-gray-700 rounded-lg px-2 py-1.5 text-sm bg-transparent" min={0} />
          </div>
        ))}
      </div>
      <button onClick={() => onCalculate?.(usage)} className="w-full bg-blue-500 text-white py-2 rounded-lg text-sm">Calculate</button>
      {plans.length > 0 && (
        <div className="grid grid-cols-3 gap-2">
          {plans.map((p, i) => (
            <div key={p.plan} className={`border rounded-xl p-3 text-center ${i === 1 ? "border-blue-500 ring-2 ring-blue-200" : "border-gray-200 dark:border-gray-700"}`}>
              <span className="font-bold text-sm block">{p.plan}</span>
              <span className="text-xl font-extrabold block">${(p.totalCents / 100).toFixed(2)}</span>
              <span className="text-[10px] text-gray-500">/month est.</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
