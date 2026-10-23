"use client";

import { useState } from "react";

interface Category { key: string; label: string; description: string; locked?: boolean; }
interface NotificationPreferencesPanelProps {
  categories: Category[]; channels: string[];
  preferences: Record<string, Record<string, boolean>>;
  onToggle: (category: string, channel: string, enabled: boolean) => void;
}

export function NotificationPreferencesPanel({ categories, channels, preferences, onToggle }: NotificationPreferencesPanelProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Notification Preferences</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b dark:border-gray-700">
              <th className="pb-2 text-left font-medium">Category</th>
              {channels.map(ch => (
                <th key={ch} className="pb-2 text-center font-medium capitalize">{ch.replace("_", " ")}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {categories.map(cat => (
              <tr key={cat.key} className="border-b dark:border-gray-700">
                <td className="py-3">
                  <p className="font-medium">{cat.label}</p>
                  <p className="text-xs text-gray-400">{cat.description}</p>
                </td>
                {channels.map(ch => (
                  <td key={ch} className="text-center">
                    <input type="checkbox" checked={preferences[cat.key]?.[ch] ?? false}
                      disabled={cat.locked} onChange={e => onToggle(cat.key, ch, e.target.checked)}
                      className="h-4 w-4 rounded accent-blue-600" />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
