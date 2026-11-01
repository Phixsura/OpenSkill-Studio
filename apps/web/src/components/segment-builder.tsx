"use client";

interface Rule { field: string; operator: string; value: unknown; label: string; }
interface SegmentBuilderProps { name: string; rules: Rule[]; matchPct: number;
  onRemoveRule: (idx: number) => void; }

const opLabels: Record<string, string> = {
  eq: "equals", gt: "greater than", lt: "less than", in: "is one of", contains: "contains",
};

export function SegmentBuilder({ name, rules, matchPct, onRemoveRule }: SegmentBuilderProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">{name}</h3>
        <span className="text-xs text-gray-400">{matchPct}% match · {rules.length} rules</span>
      </div>
      <div className="space-y-2">
        {rules.map((r, i) => (
          <div key={i} className="flex items-center justify-between rounded-lg border px-3 py-2 dark:border-gray-700">
            <div className="flex items-center gap-2 text-sm">
              <code className="font-mono text-xs bg-gray-100 px-1.5 py-0.5 rounded dark:bg-gray-800">{r.field}</code>
              <span className="text-xs text-gray-400">{opLabels[r.operator] ?? r.operator}</span>
              <span className="font-medium">{JSON.stringify(r.value)}</span>
            </div>
            <button onClick={() => onRemoveRule(i)} className="text-xs text-red-600 hover:underline">Remove</button>
          </div>
        ))}
      </div>
    </div>
  );
}
