"use client";

interface UserProfileHeaderProps { name: string; initials: string; role: string;
  plan: string; joined: string; org: string; appCount: number;
  installsDisplay: string; badges: string[]; }

export function UserProfileHeader({ name, initials, role, plan, joined, org,
  appCount, installsDisplay, badges }: UserProfileHeaderProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-6">
      <div className="flex items-center gap-4 mb-4">
        <div className="w-16 h-16 rounded-full bg-blue-500 flex items-center justify-center text-white text-2xl font-bold">
          {initials}
        </div>
        <div>
          <h2 className="text-xl font-bold">{name}</h2>
          <div className="flex gap-2 text-xs mt-1">
            <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-700 capitalize">{role}</span>
            <span className="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800 capitalize">{plan}</span>
            {org && <span className="text-gray-400">{org}</span>}
          </div>
        </div>
      </div>
      <div className="flex gap-6 text-sm text-gray-500">
        <span>📱 {appCount} apps</span>
        <span>📥 {installsDisplay} installs</span>
        <span>📅 Joined {joined}</span>
      </div>
      {badges.length > 0 && (
        <div className="flex gap-1 mt-3">
          {badges.map(b => <span key={b} className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700 capitalize">{b.replace("_", " ")}</span>)}
        </div>
      )}
    </div>
  );
}
