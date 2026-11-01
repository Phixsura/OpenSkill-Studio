"use client";

interface CategoryIconProps {
  category: string;
  size?: "sm" | "md" | "lg";
}

const ICONS: Record<string, { icon: string; label: string }> = {
  connector: { icon: "🔌", label: "Connector" },
  CONNECTOR: { icon: "🔌", label: "Connector" },
  workflow_adapter: { icon: "⚡", label: "Workflow Adapter" },
  WORKFLOW_ADAPTER: { icon: "⚡", label: "Workflow Adapter" },
  ui_extension: { icon: "🖥️", label: "UI Extension" },
  UI_EXTENSION: { icon: "🖥️", label: "UI Extension" },
  analytics: { icon: "📊", label: "Analytics" },
  ANALYTICS: { icon: "📊", label: "Analytics" },
  automation: { icon: "🤖", label: "Automation" },
  AUTOMATION: { icon: "🤖", label: "Automation" },
  content_pack: { icon: "📦", label: "Content Pack" },
  CONTENT_PACK: { icon: "📦", label: "Content Pack" },
  ecosystem_source: { icon: "🌐", label: "Ecosystem Source" },
  ECOSYSTEM_SOURCE: { icon: "🌐", label: "Ecosystem Source" },
};

const SIZES = { sm: "text-lg", md: "text-2xl", lg: "text-4xl" };

export function CategoryIcon({ category, size = "md" }: CategoryIconProps) {
  const config = ICONS[category] ?? { icon: "📦", label: category };
  return (
    <span className={SIZES[size]} title={config.label} role="img" aria-label={config.label}>
      {config.icon}
    </span>
  );
}
