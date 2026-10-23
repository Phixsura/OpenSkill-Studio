"use client";

interface ChangelogAudienceToggleProps { audience: string; onSwitch: (a: string) => void; entries: string[]; prefix: string; }

const AUDIENCES = [
  { id: "end_user", label: "Users", icon: "👤" },
  { id: "developer", label: "Developers", icon: "👨‍💻" },
  { id: "admin", label: "Admins", icon: "🔑" },
];

export function ChangelogAudienceToggle({ audience, onSwitch, entries, prefix }: ChangelogAudienceToggleProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Changelog</h3>
        <div className="flex gap-1">
          {AUDIENCES.map(a => (
            <button key={a.id} onClick={() => onSwitch(a.id)}
              className={`rounded px-2 py-1 text-xs ${audience === a.id ? "bg-blue-100 font-semibold text-blue-700" : "text-gray-500"}`}>
              {a.icon} {a.label}
            </button>
          ))}
        </div>
      </div>
      <p className="mt-3 text-xs font-medium text-gray-500">{prefix}</p>
      <ul className="mt-1 space-y-1">
        {entries.map((e, i) => <li key={i} className="text-sm text-gray-600 dark:text-gray-400">• {e}</li>)}
      </ul>
    </div>
  );
}
