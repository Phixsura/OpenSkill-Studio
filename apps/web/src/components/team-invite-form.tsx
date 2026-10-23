"use client";

import { useState } from "react";

interface TeamInviteFormProps { orgName: string; onInvite: (email: string, role: string) => void; }

const roles = [
  { id: "viewer", label: "Viewer", description: "Can view apps and data" },
  { id: "editor", label: "Editor", description: "Can edit apps and settings" },
  { id: "admin", label: "Admin", description: "Full organization access" },
];

export function TeamInviteForm({ orgName, onInvite }: TeamInviteFormProps) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("editor");

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Invite to {orgName}</h3>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Email</label>
        <input type="email" value={email} onChange={e => setEmail(e.target.value)}
          placeholder="colleague@example.com"
          className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Role</label>
        <div className="space-y-1">
          {roles.map(r => (
            <label key={r.id} className={`flex items-center gap-3 rounded border p-2 cursor-pointer ${role === r.id ? "border-blue-500" : "dark:border-gray-700"}`}>
              <input type="radio" name="role" checked={role === r.id}
                onChange={() => setRole(r.id)} className="accent-blue-600" />
              <div><p className="text-sm font-medium">{r.label}</p>
                <p className="text-xs text-gray-400">{r.description}</p></div>
            </label>
          ))}
        </div>
      </div>
      <button onClick={() => { if (email) { onInvite(email, role); setEmail(""); } }}
        className="w-full rounded bg-blue-600 py-2 text-sm text-white">Send Invite</button>
    </div>
  );
}
