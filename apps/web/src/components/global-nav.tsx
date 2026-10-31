"use client";

import { useState } from "react";

interface NavItem { id: string; label: string; href: string; icon: string; active: boolean; }
interface MenuItem { label: string; href: string; icon: string; }
interface User { name: string; initials: string; plan: string; menu: MenuItem[]; }
interface GlobalNavProps { nav: NavItem[]; user: User | null; loggedIn: boolean;
  notifications: number; onNavigate: (href: string) => void; onSearch: (q: string) => void; }

export function GlobalNav({ nav, user, loggedIn, notifications, onNavigate, onSearch }: GlobalNavProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <header className="sticky top-0 z-40 border-b bg-white/95 backdrop-blur dark:bg-gray-950/95 dark:border-gray-800">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2.5">
        <div className="flex items-center gap-5">
          <button onClick={() => onNavigate("/")} className="flex items-center gap-1.5 text-lg font-bold">🧩 OpenSkill</button>
          <nav className="hidden gap-1 md:flex">
            {nav.map(n => (
              <button key={n.id} onClick={() => onNavigate(n.href)}
                className={`rounded-lg px-3 py-1.5 text-sm ${n.active ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-900/20" : "text-gray-500 hover:text-gray-900 dark:hover:text-white"}`}>
                {n.icon} {n.label}
              </button>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <input type="search" placeholder="Search..." onChange={e => onSearch(e.target.value)}
            className="hidden rounded-lg border px-3 py-1.5 text-sm md:block dark:bg-gray-800 dark:border-gray-700 w-48" />
          {loggedIn ? (
            <div className="flex items-center gap-2">
              {notifications > 0 && (
                <button onClick={() => onNavigate("/notifications")} className="relative">
                  🔔<span className="absolute -top-1 -right-1 rounded-full bg-red-500 px-1 text-xs text-white">{notifications}</span>
                </button>
              )}
              <div className="relative">
                <button onClick={() => setMenuOpen(!menuOpen)}
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs text-white">{user?.initials}</button>
                {menuOpen && user && (
                  <div className="absolute right-0 mt-1 w-48 rounded-lg border bg-white shadow-xl dark:bg-gray-900 dark:border-gray-700">
                    <div className="border-b px-3 py-2 dark:border-gray-700">
                      <p className="text-sm font-medium">{user.name}</p>
                      <p className="text-xs text-gray-400 capitalize">{user.plan} plan</p>
                    </div>
                    {user.menu.map(m => (
                      <button key={m.href} onClick={() => { onNavigate(m.href); setMenuOpen(false); }}
                        className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
                        {m.icon} {m.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <button onClick={() => onNavigate("/login")} className="rounded-lg bg-blue-600 px-4 py-1.5 text-sm text-white">Sign In</button>
          )}
        </div>
      </div>
    </header>
  );
}
