"use client";

import { useState } from "react";

const ROLES = [
  { value: "viewer", label: "Viewer", desc: "Can view analytics only" },
  { value: "developer", label: "Developer", desc: "Can edit app and view analytics" },
  { value: "admin", label: "Admin", desc: "Can edit, publish, and manage team" },
];

interface RoleAssignmentFormProps { onAssign: (userId: string, role: string) => void; }

export function RoleAssignmentForm({ onAssign }: RoleAssignmentFormProps) {
  const [userId, setUserId] = useState("");
  const [role, setRole] = useState("viewer");

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Add Team Member</h3>
      <div className="mt-3 space-y-3">
        <input value={userId} onChange={e => setUserId(e.target.value)} placeholder="User ID or email"
          className="w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <select value={role} onChange={e => setRole(e.target.value)}
          className="w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700">
          {ROLES.map(r => <option key={r.value} value={r.value}>{r.label} — {r.desc}</option>)}
        </select>
      </div>
      <button onClick={() => { onAssign(userId, role); setUserId(""); }} disabled={!userId}
        className="mt-3 rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50">
        Add Member
      </button>
    </div>
  );
}
