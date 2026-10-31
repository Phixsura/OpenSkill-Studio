"use client";

import { useState } from "react";

interface NavItem {
  id: string;
  label: string;
  icon: string;
  badge?: number;
  children?: NavItem[];
}

export function MarketplaceNavigation({
  items,
  activeId,
  onNavigate,
  collapsed,
}: {
  items: NavItem[];
  activeId: string;
  onNavigate?: (id: string) => void;
  collapsed?: boolean;
}) {
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(
    new Set(items.filter((i) => i.children).map((i) => i.id))
  );

  const toggleGroup = (id: string) => {
    setExpandedGroups((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const renderItem = (item: NavItem, depth: number = 0) => {
    const isActive = activeId === item.id;
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedGroups.has(item.id);

    return (
      <div key={item.id}>
        <button
          onClick={() => hasChildren ? toggleGroup(item.id) : onNavigate?.(item.id)}
          className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition ${
            isActive
              ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium"
              : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          }`}
          style={{ paddingLeft: `${depth * 12 + 12}px` }}
        >
          <div className="flex items-center gap-2">
            {!collapsed && <span>{item.icon}</span>}
            {collapsed ? <span className="text-lg">{item.icon}</span> : <span>{item.label}</span>}
          </div>
          <div className="flex items-center gap-1">
            {item.badge !== undefined && item.badge > 0 && (
              <span className="bg-red-500 text-white text-xs rounded-full px-1.5 min-w-5 text-center">
                {item.badge}
              </span>
            )}
            {hasChildren && !collapsed && (
              <span className="text-xs text-gray-400">{isExpanded ? "▼" : "▶"}</span>
            )}
          </div>
        </button>
        {hasChildren && isExpanded && !collapsed && (
          <div>{item.children!.map((child) => renderItem(child, depth + 1))}</div>
        )}
      </div>
    );
  };

  return (
    <nav className={`space-y-0.5 ${collapsed ? "w-14" : "w-56"} transition-all`}>
      {items.map((item) => renderItem(item))}
    </nav>
  );
}
