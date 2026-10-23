"use client";

interface Badge { label: string; variant: string; icon: string | null;
  removable: boolean; classes: string; }
interface BadgeGroupProps { badges: Badge[]; onRemove?: (label: string) => void; }

export function BadgeGroup({ badges, onRemove }: BadgeGroupProps) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {badges.map(b => (
        <span key={b.label} className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${b.classes}`}>
          {b.icon && <span>{b.icon}</span>}
          {b.label}
          {b.removable && onRemove && (
            <button onClick={() => onRemove(b.label)} className="ml-0.5 hover:opacity-70">×</button>
          )}
        </span>
      ))}
    </div>
  );
}
