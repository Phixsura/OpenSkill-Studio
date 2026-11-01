"use client";

interface MigrationPlan {
  from_version: string;
  to_version: string;
  compat_level: "compatible" | "minor_changes" | "breaking";
  added_permissions: string[];
  removed_permissions: string[];
  added_config: string[];
  removed_config: string[];
  breaking_reasons: string[];
  requires_reauth: boolean;
  auto_migratable: boolean;
}

interface AppUpgradeCardProps {
  appName: string;
  appIcon: string;
  plan: MigrationPlan;
  onUpgrade: () => void;
  onDismiss: () => void;
  upgrading?: boolean;
}

const COMPAT_STYLES: Record<string, { label: string; color: string; bg: string; border: string }> =
  {
    compatible: {
      label: "Compatible",
      color: "text-green-700 dark:text-green-300",
      bg: "bg-green-50 dark:bg-green-900/10",
      border: "border-green-200 dark:border-green-800",
    },
    minor_changes: {
      label: "Minor Changes",
      color: "text-blue-700 dark:text-blue-300",
      bg: "bg-blue-50 dark:bg-blue-900/10",
      border: "border-blue-200 dark:border-blue-800",
    },
    breaking: {
      label: "Breaking",
      color: "text-red-700 dark:text-red-300",
      bg: "bg-red-50 dark:bg-red-900/10",
      border: "border-red-200 dark:border-red-800",
    },
  };

function ChangeList({
  title,
  items,
  icon,
  color,
}: {
  title: string;
  items: string[];
  icon: string;
  color: string;
}) {
  if (items.length === 0) return null;
  return (
    <div>
      <p className="text-[10px] font-semibold uppercase text-gray-400">{title}</p>
      <ul className="mt-1 space-y-0.5">
        {items.map((item) => (
          <li key={item} className={`flex items-center gap-1.5 text-xs ${color}`}>
            <span>{icon}</span>
            <code>{item}</code>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function AppUpgradeCard({
  appName,
  appIcon,
  plan,
  onUpgrade,
  onDismiss,
  upgrading,
}: AppUpgradeCardProps) {
  const style = COMPAT_STYLES[plan.compat_level] ?? COMPAT_STYLES.breaking;
  const hasChanges =
    plan.added_permissions.length > 0 ||
    plan.removed_permissions.length > 0 ||
    plan.added_config.length > 0 ||
    plan.removed_config.length > 0;

  return (
    <div className={`rounded-xl border p-4 ${style.border} ${style.bg}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{appIcon}</span>
          <div>
            <h3 className="font-semibold">{appName}</h3>
            <p className="text-xs text-gray-500">
              {plan.from_version} → {plan.to_version}
            </p>
          </div>
        </div>
        <span
          className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${style.color} ${style.bg}`}
        >
          {style.label}
        </span>
      </div>

      {/* Breaking warnings */}
      {plan.breaking_reasons.length > 0 && (
        <div className="mt-3 rounded-md bg-red-100 px-3 py-2 dark:bg-red-900/20">
          <p className="text-xs font-semibold text-red-700 dark:text-red-400">⚠ Breaking Changes</p>
          <ul className="mt-1 space-y-0.5">
            {plan.breaking_reasons.map((r, i) => (
              <li key={i} className="text-xs text-red-600 dark:text-red-400">
                • {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Changes */}
      {hasChanges && (
        <div className="mt-3 space-y-2">
          <ChangeList
            title="New Permissions"
            items={plan.added_permissions}
            icon="+"
            color="text-green-600 dark:text-green-400"
          />
          <ChangeList
            title="Removed Permissions"
            items={plan.removed_permissions}
            icon="−"
            color="text-red-600 dark:text-red-400"
          />
          <ChangeList
            title="New Config Fields"
            items={plan.added_config}
            icon="+"
            color="text-blue-600 dark:text-blue-400"
          />
          <ChangeList
            title="Removed Config Fields"
            items={plan.removed_config}
            icon="−"
            color="text-orange-600 dark:text-orange-400"
          />
        </div>
      )}

      {/* Consent notice */}
      {plan.requires_reauth && (
        <p className="mt-3 text-xs text-amber-700 dark:text-amber-400">
          🔑 New permissions require your approval before upgrade.
        </p>
      )}

      {/* Actions */}
      <div className="mt-4 flex gap-2">
        <button
          onClick={onUpgrade}
          disabled={upgrading}
          className={`rounded-md px-4 py-2 text-sm font-medium text-white ${plan.compat_level === "breaking" ? "bg-red-600 hover:bg-red-700" : "bg-blue-600 hover:bg-blue-700"} disabled:opacity-50`}
        >
          {upgrading
            ? "Upgrading…"
            : plan.compat_level === "breaking"
              ? "Force Upgrade"
              : "Upgrade"}
        </button>
        <button
          onClick={onDismiss}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-white/50 dark:border-gray-600 dark:text-gray-400"
        >
          Not Now
        </button>
      </div>
    </div>
  );
}
