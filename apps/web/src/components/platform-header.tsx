"use client";

interface HeaderUser { name: string; initials: string; avatarUrl: string; }
interface PlatformHeaderProps { user: HeaderUser; orgName: string | null;
  unreadCount: number; planBadge: string; navLinks: { label: string; path: string }[];
  onNavigate: (path: string) => void; }

export function PlatformHeader({ user, orgName, unreadCount, planBadge, navLinks, onNavigate }: PlatformHeaderProps) {
  return (
    <header className="flex items-center justify-between px-4 py-2.5 border-b dark:border-gray-700">
      <div className="flex items-center gap-4">
        <span className="font-bold text-lg">⚡ OpenSkill</span>
        <nav className="flex gap-1">
          {navLinks.map(l => (
            <button key={l.path} onClick={() => onNavigate(l.path)}
              className="text-sm px-2.5 py-1 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded transition">{l.label}</button>
          ))}
        </nav>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700 font-bold">{planBadge}</span>
        <div className="relative">
          <span className="text-lg cursor-pointer">🔔</span>
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 text-[10px] px-1 rounded-full bg-red-500 text-white font-bold">{unreadCount}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="w-7 h-7 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center font-bold">{user.initials}</span>
          <span className="text-sm font-medium">{user.name}</span>
        </div>
      </div>
    </header>
  );
}
