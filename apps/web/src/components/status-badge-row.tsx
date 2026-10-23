"use client";

interface Badge { svgUrl: string; label: string; value: string; color: string; }
interface StatusBadgeRowProps { badges: Badge[]; }

export function StatusBadgeRow({ badges }: StatusBadgeRowProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      {badges.map((b, i) => (
        <div key={i} className="flex items-center rounded overflow-hidden text-xs font-medium" title={`${b.label}: ${b.value}`}>
          <span className="bg-gray-600 px-2 py-0.5 text-white">{b.label}</span>
          <span className="px-2 py-0.5 text-white" style={{
            backgroundColor: b.color === "brightgreen" ? "#4c1" : b.color === "red" ? "#e05d44" :
              b.color === "yellow" ? "#dfb317" : b.color === "blue" ? "#007ec6" : "#9f9f9f"
          }}>{b.value}</span>
        </div>
      ))}
    </div>
  );
}
