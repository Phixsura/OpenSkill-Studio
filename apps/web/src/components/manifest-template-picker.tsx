"use client";

import { useState } from "react";

const TEMPLATES = [
  { key: "connector", icon: "🔌", label: "Connector", desc: "LMS, CRM, HRIS integrations" },
  { key: "automation", icon: "🤖", label: "Automation", desc: "Event-driven workflows" },
  { key: "analytics", icon: "📊", label: "Analytics", desc: "Reporting and insights" },
  { key: "ui_extension", icon: "🖥️", label: "UI Extension", desc: "Dashboard cards, panels" },
  { key: "ecosystem_source", icon: "🌐", label: "Ecosystem Source", desc: "External data sources" },
];

interface ManifestTemplatePickerProps {
  onSelect: (category: string) => void;
  selected?: string;
}

export function ManifestTemplatePicker({ onSelect, selected }: ManifestTemplatePickerProps) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {TEMPLATES.map((t) => (
        <button
          key={t.key}
          onClick={() => onSelect(t.key)}
          className={`rounded-lg border p-4 text-left transition-colors hover:border-blue-400 ${
            selected === t.key
              ? "border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-900/20"
              : "border-gray-200 dark:border-gray-700"
          }`}
        >
          <div className="mb-1 text-2xl">{t.icon}</div>
          <h4 className="font-semibold">{t.label}</h4>
          <p className="text-sm text-gray-500 dark:text-gray-400">{t.desc}</p>
        </button>
      ))}
    </div>
  );
}
