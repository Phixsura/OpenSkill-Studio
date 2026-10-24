"use client";

interface Label { name: string; color: string; count: number; }
interface LabelPickerProps { labels: Label[]; selected: Set<string>; onToggle: (name: string) => void; }

export function LabelPicker({ labels, selected, onToggle }: LabelPickerProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold">Labels</h3>
      <div className="flex flex-wrap gap-1.5">
        {labels.map(l => (
          <button key={l.name} onClick={() => onToggle(l.name)}
            className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium transition ${selected.has(l.name) ? "ring-2 ring-offset-1" : "opacity-70 hover:opacity-100"}`}
            style={{ backgroundColor: l.color + "20", color: l.color, borderColor: l.color }}>
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: l.color }} />
            {l.name}
            {l.count > 0 && <span className="text-xs opacity-60">{l.count}</span>}
          </button>
        ))}
      </div>
    </div>
  );
}
