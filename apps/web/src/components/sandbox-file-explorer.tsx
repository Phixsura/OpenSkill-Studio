"use client";

import { useState } from "react";

interface FileEntry {
  name: string;
  type: "file" | "directory";
  size: number;
  path: string;
}

interface StorageUsage {
  usedBytes: number;
  maxBytes: number;
  usagePercent: number;
}

const fileIcons: Record<string, string> = {
  js: "📜", ts: "📘", py: "🐍", json: "📋", md: "📝",
  txt: "📄", html: "🌐", css: "🎨", yaml: "⚙️", yml: "⚙️",
};

function getIcon(name: string, type: string): string {
  if (type === "directory") return "📁";
  const ext = name.split(".").pop() || "";
  return fileIcons[ext] || "📄";
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / 1048576).toFixed(1)}MB`;
}

export function SandboxFileExplorer({
  entries,
  currentPath,
  usage,
  onNavigate,
  onDelete,
  onUpload,
}: {
  entries: FileEntry[];
  currentPath: string;
  usage: StorageUsage;
  onNavigate?: (path: string) => void;
  onDelete?: (path: string) => void;
  onUpload?: () => void;
}) {
  const dirs = entries.filter((e) => e.type === "directory");
  const files = entries.filter((e) => e.type === "file");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📂 Sandbox Files</h2>
        <button onClick={onUpload} className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">Upload</button>
      </div>

      <div className="flex items-center gap-2 text-sm">
        <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded flex-1">{currentPath}</code>
        {currentPath !== "/" && (
          <button onClick={() => {
            const parent = currentPath.split("/").slice(0, -1).join("/") || "/";
            onNavigate?.(parent);
          }} className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">⬆ Up</button>
        )}
      </div>

      <div className="rounded-lg border dark:border-gray-700 overflow-hidden">
        {[...dirs, ...files].map((entry) => (
          <div key={entry.path} className="flex items-center justify-between px-3 py-2 border-b dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <div className="flex items-center gap-2 flex-1 min-w-0 cursor-pointer"
              onClick={() => entry.type === "directory" ? onNavigate?.(entry.path) : undefined}>
              <span>{getIcon(entry.name, entry.type)}</span>
              <span className={`text-sm truncate ${entry.type === "directory" ? "font-semibold" : ""}`}>{entry.name}</span>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-xs text-gray-400">{entry.type === "file" ? formatSize(entry.size) : ""}</span>
              <button onClick={() => onDelete?.(entry.path)} className="text-xs text-red-500 hover:text-red-700">✕</button>
            </div>
          </div>
        ))}
        {entries.length === 0 && (
          <div className="px-3 py-4 text-center text-sm text-gray-500">Empty directory</div>
        )}
      </div>

      <div className="text-xs text-gray-500">
        Storage: {formatSize(usage.usedBytes)} / {formatSize(usage.maxBytes)} ({usage.usagePercent}%)
        <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full mt-1 overflow-hidden">
          <div className={`h-full rounded-full ${usage.usagePercent > 80 ? "bg-red-500" : "bg-blue-500"}`}
            style={{ width: `${Math.min(usage.usagePercent, 100)}%` }} />
        </div>
      </div>
    </div>
  );
}
