"use client";

import { useState } from "react";

interface Invite { invite_id: string; email: string; role: string; status: string; }
interface TeamInviteManagerProps { invites: Invite[]; onInvite: (email: string, role: string) => void;
  onRevoke: (id: string) => void; }

export function TeamInviteManager({ invites, onInvite, onRevoke }: TeamInviteManagerProps) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("developer");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Team Invites</h2>
      <div className="flex gap-2">
        <input value={email} onChange={e => setEmail(e.target.value)} placeholder="email@example.com"
          className="flex-1 rounded border px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <select value={role} onChange={e => setRole(e.target.value)}
          className="rounded border px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700">
          <option value="developer">Developer</option>
          <option value="viewer">Viewer</option>
          <option value="admin">Admin</option>
        </select>
        <button onClick={() => { onInvite(email, role); setEmail(""); }}
          className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Invite</button>
      </div>
      {invites.length > 0 && (
        <div className="space-y-1.5">
          {invites.map(inv => (
            <div key={inv.invite_id} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
              <div>
                <span className="text-sm">{inv.email}</span>
                <span className="ml-2 rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{inv.role}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-yellow-500">{inv.status}</span>
                <button onClick={() => onRevoke(inv.invite_id)} className="text-xs text-red-500">Revoke</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
