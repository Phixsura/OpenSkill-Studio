"use client";

interface CostAllocationDashboardProps { totalCost: string; byTeam: Record<string, number>;
  byProject: Record<string, number>; trend: string; pctChange: number; }

export function CostAllocationDashboard({ totalCost, byTeam, byProject, trend, pctChange }: CostAllocationDashboardProps) {
  const teams = Object.entries(byTeam).sort((a, b) => b[1] - a[1]);
  const projects = Object.entries(byProject).sort((a, b) => b[1] - a[1]);
  const maxTeam = Math.max(...teams.map(([, c]) => c), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💰 Cost Allocation</h3>
        <div className="text-right">
          <div className="text-lg font-bold">{totalCost}</div>
          <div className={`text-[10px] ${trend === "up" ? "text-red-500" : "text-green-600"}`}>
            {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} {pctChange}%
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700">
        <div className="p-3">
          <div className="text-xs text-gray-400 mb-2">By Team</div>
          {teams.map(([team, cost]) => (
            <div key={team} className="mb-1.5">
              <div className="flex justify-between text-xs mb-0.5">
                <span>{team}</span><span className="text-gray-400">${cost}</span>
              </div>
              <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(cost / maxTeam) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
        <div className="p-3">
          <div className="text-xs text-gray-400 mb-2">By Project</div>
          {projects.map(([proj, cost]) => (
            <div key={proj} className="flex justify-between text-xs py-0.5">
              <span>{proj}</span><span className="text-gray-400">${cost}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
