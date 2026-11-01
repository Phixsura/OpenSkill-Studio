"use client";

interface FieldChange {
  field_path: string;
  kind: "added" | "removed" | "modified" | "unchanged";
  severity: "none" | "patch" | "minor" | "breaking";
  old_value: unknown;
  new_value: unknown;
}

interface ManifestDiffData {
  from_version: string;
  to_version: string;
  changes: FieldChange[];
  added_permissions: string[];
  removed_permissions: string[];
  added_config_fields: string[];
  removed_config_fields: string[];
  added_surfaces: string[];
  removed_surfaces: string[];
  has_breaking: boolean;
  summary: string;
}

interface ManifestDiffViewerProps {
  diff: ManifestDiffData;
}

const KIND_STYLES: Record<string, { icon: string; color: string; bg: string }> = {
  added: {
    icon: "+",
    color: "text-green-700 dark:text-green-300",
    bg: "bg-green-50 dark:bg-green-900/10",
  },
  removed: {
    icon: "−",
    color: "text-red-700 dark:text-red-300",
    bg: "bg-red-50 dark:bg-red-900/10",
  },
  modified: {
    icon: "~",
    color: "text-yellow-700 dark:text-yellow-300",
    bg: "bg-yellow-50 dark:bg-yellow-900/10",
  },
  unchanged: { icon: " ", color: "text-gray-400", bg: "" },
};

const SEV_BADGE: Record<string, { label: string; color: string }> = {
  breaking: {
    label: "BREAKING",
    color: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300",
  },
  minor: {
    label: "MINOR",
    color: "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300",
  },
  patch: { label: "PATCH", color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400" },
  none: { label: "", color: "" },
};

function formatValue(v: unknown): string {
  if (v === null || v === undefined) return "—";
  if (Array.isArray(v)) return v.join(", ");
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

function ChipGroup({ label, items, color }: { label: string; items: string[]; color: string }) {
  if (items.length === 0) return null;
  return (
    <div className="flex items-start gap-2 text-xs">
      <span className="shrink-0 font-medium text-gray-500">{label}:</span>
      <div className="flex flex-wrap gap-1">
        {items.map((item) => (
          <code key={item} className={`rounded px-1.5 py-0.5 text-[10px] ${color}`}>
            {item}
          </code>
        ))}
      </div>
    </div>
  );
}

export function ManifestDiffViewer({ diff }: ManifestDiffViewerProps) {
  const realChanges = diff.changes.filter((c) => c.kind !== "unchanged");

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <h3 className="font-semibold">Manifest Diff</h3>
        <p className="text-xs text-gray-500">
          {diff.from_version} → {diff.to_version} • {diff.summary}
        </p>
      </div>

      {/* Breaking warning */}
      {diff.has_breaking && (
        <div className="bg-red-50 px-4 py-2 text-xs font-medium text-red-700 dark:bg-red-900/10 dark:text-red-400">
          ⚠️ Contains breaking changes — review carefully before upgrading
        </div>
      )}

      {/* Permission/config/surface chips */}
      <div className="space-y-1.5 border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <ChipGroup
          label="+Permissions"
          items={diff.added_permissions}
          color="bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300"
        />
        <ChipGroup
          label="−Permissions"
          items={diff.removed_permissions}
          color="bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300"
        />
        <ChipGroup
          label="+Config"
          items={diff.added_config_fields}
          color="bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
        />
        <ChipGroup
          label="−Config"
          items={diff.removed_config_fields}
          color="bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-300"
        />
        <ChipGroup
          label="+Surfaces"
          items={diff.added_surfaces}
          color="bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300"
        />
        <ChipGroup
          label="−Surfaces"
          items={diff.removed_surfaces}
          color="bg-pink-100 text-pink-700 dark:bg-pink-900/20 dark:text-pink-300"
        />
      </div>

      {/* Field changes */}
      {realChanges.length === 0 ? (
        <div className="py-6 text-center text-sm text-gray-500">No field changes</div>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {realChanges.map((c) => {
            const style = KIND_STYLES[c.kind] ?? KIND_STYLES.modified;
            const sev = SEV_BADGE[c.severity] ?? SEV_BADGE.none;
            return (
              <div key={c.field_path} className={`flex items-start gap-2 px-4 py-2 ${style.bg}`}>
                <span className={`mt-0.5 font-mono text-sm font-bold ${style.color}`}>
                  {style.icon}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <code className="text-xs font-medium">{c.field_path}</code>
                    {sev.label && (
                      <span className={`rounded px-1 py-0.5 text-[9px] font-bold ${sev.color}`}>
                        {sev.label}
                      </span>
                    )}
                  </div>
                  {c.kind === "modified" && (
                    <div className="mt-0.5 text-[10px]">
                      <span className="text-red-500 line-through">{formatValue(c.old_value)}</span>
                      <span className="mx-1 text-gray-400">→</span>
                      <span className="text-green-600">{formatValue(c.new_value)}</span>
                    </div>
                  )}
                  {c.kind === "added" && (
                    <p className="mt-0.5 text-[10px] text-green-600">{formatValue(c.new_value)}</p>
                  )}
                  {c.kind === "removed" && (
                    <p className="mt-0.5 text-[10px] text-red-500 line-through">
                      {formatValue(c.old_value)}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
