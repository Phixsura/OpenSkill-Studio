"use client";

interface PermissionListProps {
  permissions: string[];
  maxVisible?: number;
}

const PERM_ICONS: Record<string, string> = {
  read: "👁️",
  write: "✏️",
  subscribe: "🔔",
  extend: "🧩",
  export: "📤",
  run: "⚡",
};

export function PermissionList({ permissions, maxVisible = 10 }: PermissionListProps) {
  const visible = permissions.slice(0, maxVisible);
  const remaining = permissions.length - maxVisible;

  return (
    <div className="flex flex-wrap gap-1.5">
      {visible.map((perm) => {
        const [action] = perm.split(":");
        const icon = PERM_ICONS[action ?? ""] ?? "🔑";
        return (
          <span
            key={perm}
            className="inline-flex items-center gap-1 rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-700"
            title={perm}
          >
            <span>{icon}</span>
            <code>{perm}</code>
          </span>
        );
      })}
      {remaining > 0 && (
        <span className="inline-flex items-center rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-500 dark:bg-gray-700">
          +{remaining} more
        </span>
      )}
    </div>
  );
}
