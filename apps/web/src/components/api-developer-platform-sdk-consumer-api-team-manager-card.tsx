"use client";

import { useState } from "react";

interface Member { userId: string; role: string; }
interface TeamInfo { teamId: string; name: string; members: Member[]; }

const ROLE_COLOR: Record<string, string> = {
  owner: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300",
  admin: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  developer: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  viewer: "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400",
};

export default function TeamManagerCard() {
  const [team] = useState<TeamInfo>({
    teamId: "t1", name: "Platform Team",
    members: [
      { userId: "alice", role: "owner" },
      { userId: "bob", role: "admin" },
      { userId: "charlie", role: "developer" },
      { userId: "diana", role: "viewer" },
    ],
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Team Manager
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Team-based API access with roles
      </p>

      <div className="mt-3 text-sm font-medium text-zinc-700 dark:text-zinc-300">{team.name}</div>

      <div className="mt-3 space-y-2">
        {team.members.map((m) => (
          <div key={m.userId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <span className="text-sm text-zinc-800 dark:text-zinc-200">{m.userId}</span>
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${ROLE_COLOR[m.role] ?? ""}`}>{m.role}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {team.members.length} members
      </div>
    </div>
  );
}
