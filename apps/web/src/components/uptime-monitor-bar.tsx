"use client";

interface Day { date: string; status: string; color: string; }
interface UptimeMonitorBarProps { serviceName: string; days: Day[];
  uptimePct: number; nines: string; }

const dotColors: Record<string, string> = {
  green: "bg-green-500", yellow: "bg-yellow-500", red: "bg-red-500", gray: "bg-gray-300",
};

export function UptimeMonitorBar({ serviceName, days, uptimePct, nines }: UptimeMonitorBarProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{serviceName}</span>
        <span className={`text-xs font-medium ${uptimePct >= 99.9 ? "text-green-600" : uptimePct >= 99 ? "text-yellow-600" : "text-red-600"}`}>{nines}</span>
      </div>
      <div className="flex gap-px">
        {days.map((d, i) => (
          <div key={i} title={`${d.date}: ${d.status}`}
            className={`h-8 flex-1 rounded-sm ${dotColors[d.color] ?? "bg-gray-300"}`} />
        ))}
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>{days[0]?.date}</span>
        <span>{days.length} days</span>
        <span>{days[days.length - 1]?.date}</span>
      </div>
    </div>
  );
}
