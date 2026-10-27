"use client";

import { useState } from "react";

interface DependencyNode {
  name: string;
  version: string;
  depth: number;
  children: DependencyNode[];
  status?: "resolved" | "missing" | "conflict";
  constraint?: string;
}

interface DependencyTreeViewProps {
  root: DependencyNode;
  totalPackages: number;
  onSelect?: (name: string) => void;
}

const STATUS_STYLES: Record<string, { icon: string; color: string }> = {
  resolved: { icon: "✓", color: "text-green-600 dark:text-green-400" },
  missing: { icon: "✗", color: "text-red-600 dark:text-red-400" },
  conflict: { icon: "⚠", color: "text-yellow-600 dark:text-yellow-400" },
};

function TreeNode({
  node,
  onSelect,
  isLast,
  prefix,
}: {
  node: DependencyNode;
  onSelect?: (name: string) => void;
  isLast: boolean;
  prefix: string;
}) {
  const [expanded, setExpanded] = useState(node.depth < 3);
  const hasChildren = node.children.length > 0;
  const connector = isLast ? "└── " : "├── ";
  const childPrefix = prefix + (isLast ? "    " : "│   ");
  const statusStyle = STATUS_STYLES[node.status ?? "resolved"];

  return (
    <div>
      <div className="flex items-center gap-1 font-mono text-sm leading-6">
        <span className="select-none text-gray-400 dark:text-gray-600" aria-hidden>
          {prefix}
          {connector}
        </span>
        {hasChildren && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mr-0.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            aria-label={expanded ? "Collapse" : "Expand"}
          >
            {expanded ? "▾" : "▸"}
          </button>
        )}
        <button onClick={() => onSelect?.(node.name)} className="hover:underline">
          <span className="font-medium">{node.name}</span>
          <span className="ml-1 text-gray-400">@{node.version}</span>
        </button>
        {node.constraint && <span className="ml-1 text-xs text-gray-400">({node.constraint})</span>}
        <span className={`ml-1 text-xs ${statusStyle.color}`}>{statusStyle.icon}</span>
      </div>

      {expanded && hasChildren && (
        <div>
          {node.children.map((child, i) => (
            <TreeNode
              key={child.name}
              node={child}
              onSelect={onSelect}
              isLast={i === node.children.length - 1}
              prefix={childPrefix}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function countNodes(node: DependencyNode): number {
  return 1 + node.children.reduce((sum, c) => sum + countNodes(c), 0);
}

export function DependencyTreeView({ root, totalPackages, onSelect }: DependencyTreeViewProps) {
  const treeSize = countNodes(root);
  const missingCount = countByStatus(root, "missing");
  const conflictCount = countByStatus(root, "conflict");

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <h3 className="font-semibold">Dependency Tree</h3>
        <div className="mt-1 flex gap-3 text-xs text-gray-500">
          <span>{totalPackages} packages</span>
          <span>{treeSize} nodes</span>
          {missingCount > 0 && <span className="text-red-600">{missingCount} missing</span>}
          {conflictCount > 0 && <span className="text-yellow-600">{conflictCount} conflicts</span>}
          {missingCount === 0 && conflictCount === 0 && (
            <span className="text-green-600">All resolved</span>
          )}
        </div>
      </div>

      {/* Tree */}
      <div className="overflow-x-auto p-4">
        <div className="font-mono text-sm leading-6">
          <div className="flex items-center gap-1">
            <span className="font-medium">{root.name}</span>
            <span className="text-gray-400">@{root.version}</span>
          </div>
          {root.children.map((child, i) => (
            <TreeNode
              key={child.name}
              node={child}
              onSelect={onSelect}
              isLast={i === root.children.length - 1}
              prefix=""
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function countByStatus(node: DependencyNode, status: string): number {
  let count = node.status === status ? 1 : 0;
  for (const child of node.children) {
    count += countByStatus(child, status);
  }
  return count;
}
