"use client";

interface InputSecurityBadgeProps { checks: { name: string; safe: boolean; details?: string }[]; }

export function InputSecurityBadge({ checks }: InputSecurityBadgeProps) {
  const allSafe = checks.every(c => c.safe);
  return (
    <div className={`rounded-lg border p-3 ${allSafe ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20" : "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20"}`}>
      <div className="flex items-center gap-2">
        <span>{allSafe ? "🛡️" : "⚠️"}</span>
        <span className={`text-sm font-medium ${allSafe ? "text-green-700" : "text-red-700"}`}>
          {allSafe ? "Input Validated" : "Security Issues Detected"}
        </span>
      </div>
      <ul className="mt-2 space-y-0.5">
        {checks.map(c => (
          <li key={c.name} className="flex items-center gap-1 text-xs">
            <span>{c.safe ? "✅" : "❌"}</span>
            <span>{c.name}</span>
            {c.details && !c.safe && <span className="text-red-500">— {c.details}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
