"use client";

interface DepMatrixGridProps { services: string[]; matrix: Record<string, Record<string, boolean>>;
  totalDeps: number; densityPct: number; }

export function DepMatrixGrid({ services, matrix, totalDeps, densityPct }: DepMatrixGridProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Dependency Matrix</h3>
        <span className="text-xs text-gray-400">{totalDeps} deps · {densityPct}% density</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-[10px]">
          <thead><tr>
            <th className="p-1.5" />
            {services.map(s => <th key={s} className="p-1.5 font-mono text-gray-400 -rotate-45">{s}</th>)}
          </tr></thead>
          <tbody>
            {services.map(from => (
              <tr key={from}>
                <td className="p-1.5 font-mono font-medium">{from}</td>
                {services.map(to => {
                  const dep = matrix[from]?.[to];
                  const isSelf = from === to;
                  return (
                    <td key={to} className={`p-1.5 text-center ${isSelf ? "bg-gray-100 dark:bg-gray-800" : ""}`}>
                      {isSelf ? "—" : dep ? "●" : ""}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
