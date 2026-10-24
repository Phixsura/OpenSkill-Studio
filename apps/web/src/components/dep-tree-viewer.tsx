"use client";

interface TreeNode { name: string; children: TreeNode[]; circular?: boolean; }
interface DepTreeViewerProps { tree: TreeNode; totalNodes: number; maxDepth: number; root: string; }

function TreeItem({ node, indent }: { node: TreeNode; indent: number }) {
  return (
    <>
      <div className="text-xs py-0.5" style={{ paddingLeft: `${indent * 16}px` }}>
        {indent > 0 && <span className="text-gray-300 mr-1">└─</span>}
        <span className={`font-mono ${node.circular ? "text-red-500" : ""}`}>
          {node.name} {node.circular ? "🔄" : ""}
        </span>
      </div>
      {node.children.map(c => <TreeItem key={c.name + indent} node={c} indent={indent + 1} />)}
    </>
  );
}

export function DepTreeViewer({ tree, totalNodes, maxDepth, root }: DepTreeViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌳 Dependency Tree</h3>
        <span className="text-xs text-gray-400">{totalNodes} nodes · depth {maxDepth} · root: {root}</span>
      </div>
      <div className="p-3 font-mono max-h-48 overflow-y-auto">
        <TreeItem node={tree} indent={0} />
      </div>
    </div>
  );
}
