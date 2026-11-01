"use client";

import { useState } from "react";

interface PermissionGrant {
  id: string;
  permission: string;
  status: "pending" | "granted" | "denied" | "revoked";
  isDangerous: boolean;
}

const permissionIcons: Record<string, string> = {
  "file:read": "📄", "file:write": "✏️", "network:outbound": "🌐",
  "network:inbound": "📡", "clipboard:read": "📋", "clipboard:write": "📋",
  "notification:send": "🔔", "camera:access": "📷", "microphone:access": "🎤",
  "geolocation:access": "📍", "storage:local": "💾", "storage:cloud": "☁️",
  "ipc:send": "📤", "ipc:receive": "📥", "exec:subprocess": "⚙️",
};

const statusStyles: Record<string, { color: string; label: string }> = {
  pending: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", label: "Pending" },
  granted: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", label: "Granted" },
  denied: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", label: "Denied" },
  revoked: { color: "bg-gray-200 text-gray-500 dark:bg-gray-800", label: "Revoked" },
};

export function SandboxPermissionsPanel({
  grants,
  extensionName,
  onApprove,
  onDeny,
  onRevoke,
}: {
  grants: PermissionGrant[];
  extensionName: string;
  onApprove?: (id: string) => void;
  onDeny?: (id: string) => void;
  onRevoke?: (id: string) => void;
}) {
  const pending = grants.filter((g) => g.status === "pending").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔐 {extensionName} Permissions</h2>
        {pending > 0 && (
          <span className="text-xs bg-yellow-500 text-white px-2 py-1 rounded-full">{pending} pending</span>
        )}
      </div>

      <div className="space-y-2">
        {grants.map((grant) => {
          const icon = permissionIcons[grant.permission] || "🔑";
          const style = statusStyles[grant.status];
          return (
            <div key={grant.id} className="rounded-xl border dark:border-gray-700 p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span>{icon}</span>
                <code className="text-sm">{grant.permission}</code>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${style.color}`}>{style.label}</span>
                {grant.isDangerous && (
                  <span className="text-xs text-red-500 font-medium">⚠ Dangerous</span>
                )}
              </div>
              <div className="flex gap-1">
                {grant.status === "pending" && (
                  <>
                    <button onClick={() => onApprove?.(grant.id)}
                      className="text-xs bg-green-600 text-white px-2 py-1 rounded">Allow</button>
                    <button onClick={() => onDeny?.(grant.id)}
                      className="text-xs bg-red-600 text-white px-2 py-1 rounded">Deny</button>
                  </>
                )}
                {grant.status === "granted" && (
                  <button onClick={() => onRevoke?.(grant.id)}
                    className="text-xs bg-gray-600 text-white px-2 py-1 rounded">Revoke</button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
