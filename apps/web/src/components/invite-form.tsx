"use client";

import { useState } from "react";

interface InviteFormProps { onInvite: (email: string, role: string) => void; }

export function InviteForm({ onInvite }: InviteFormProps) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("member");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) { onInvite(email, role); setEmail(""); }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="colleague@company.com"
        className="flex-1 rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800" required />
      <select value={role} onChange={e => setRole(e.target.value)}
        className="rounded border px-2 py-2 text-sm dark:border-gray-600 dark:bg-gray-800">
        <option value="member">Member</option>
        <option value="admin">Admin</option>
      </select>
      <button type="submit" className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">Invite</button>
    </form>
  );
}
