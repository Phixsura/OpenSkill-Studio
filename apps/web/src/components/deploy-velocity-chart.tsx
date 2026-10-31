"use client";

interface DeployVelocityChartProps { total: number; perDay: number; successRate: number;
  fastestTeam: string | null; byTeam: Record<string, number>; byEnvironment: Record<string, number>; }

export function DeployVelocityChart({ total, perDay, successRate, fastestTeam, byTeam, byEnvironment }: DeployVelocityChartProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Deploy Velocity</h3>
        <span className="text-xs text-gray-400">{total} deploys · {perDay}/day · {successRate}%</span>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700 p-3 text-xs">
        <div>
          <div className="text-gray-400 mb-1">By Team {fastestTeam && `(fastest: ${fastestTeam})`}</div>
          {Object.entries(byTeam).map(([t, c]) => (
            <div key={t} className="flex justify-between py-0.5"><span>{t}</span><span className="text-gray-400">{c}</span></div>
          ))}
        </div>
        <div className="pl-3">
          <div className="text-gray-400 mb-1">By Environment</div>
          {Object.entries(byEnvironment).map(([e, c]) => (
            <div key={e} className="flex justify-between py-0.5"><span>{e}</span><span className="text-gray-400">{c}</span></div>
          ))}
        </div>
      </div>
    </div>
  );
}
