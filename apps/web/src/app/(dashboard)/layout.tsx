"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { useTheme } from "next-themes";

import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { NotificationBell } from "@/components/notification-bell";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, clearAuth } = useAuthStore();
  const { theme, setTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  // Close mobile sidebar on Escape key
  useEffect(() => {
    if (!sidebarOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSidebarOpen(false);
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [sidebarOpen]);

  // Redirect to login when auth is lost (logout, session expiry, bfcache)
  // Track: once authenticated, redirect if it becomes false
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const wasAuthenticated = useRef(false);
  useEffect(() => {
    if (isAuthenticated) {
      wasAuthenticated.current = true;
    } else if (wasAuthenticated.current && mounted) {
      // Was logged in, now logged out → redirect
      router.replace(`/login?redirect=${encodeURIComponent(pathname)}`);
    }
  }, [isAuthenticated, mounted, router, pathname]);

  const handleLogout = async () => {
    try {
      const token = useAuthStore.getState().accessToken;
      await api("/auth/logout", {
        method: "POST",
        credentials: "include",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
    } catch {
      // Logout should succeed even if the API call fails
    } finally {
      clearAuth();
      router.push("/login");
    }
  };

  const closeSidebar = () => setSidebarOpen(false);

  const navLinks = (
    <>
      <NavLink href="/dashboard" active={pathname === "/dashboard"} onClick={closeSidebar}>Dashboard</NavLink>
      <NavLink href="/dashboard/orgs" active={pathname.startsWith("/dashboard/orgs")} onClick={closeSidebar}>Organizations</NavLink>
      <NavLink href="/dashboard/skills" active={pathname.startsWith("/dashboard/skills")} onClick={closeSidebar}>Skills</NavLink>
      <NavLink href="/dashboard/projects" active={pathname.startsWith("/dashboard/projects")} onClick={closeSidebar}>Projects</NavLink>
      <NavLink href="/dashboard/portfolio" active={pathname.startsWith("/dashboard/portfolio")} onClick={closeSidebar}>Portfolio</NavLink>
      <NavLink href="/dashboard/settings" active={pathname === "/dashboard/settings"} onClick={closeSidebar}>Settings</NavLink>
    </>
  );

  const userSection = (
    <div className="border-t p-4">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[hsl(var(--primary))] text-sm font-medium text-[hsl(var(--primary-foreground))]">
          {mounted ? (user?.display_name?.charAt(0)?.toUpperCase() ?? "?") : "·"}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium">
            {mounted ? (user?.display_name ?? "User") : " "}
          </p>
          <p className="truncate text-xs text-[hsl(var(--muted-foreground))]">
            {mounted ? user?.email : " "}
          </p>
        </div>
      </div>
      <button
        onClick={handleLogout}
        className="mt-3 w-full rounded-md border px-3 py-1.5 text-sm hover:bg-[hsl(var(--secondary))]"
      >
        Log out
      </button>
    </div>
  );

  return (
    <div className="flex h-screen">
      {/* Mobile header */}
      <div className="fixed left-0 right-0 top-0 z-40 flex items-center border-b bg-[hsl(var(--card))] px-4 py-3 md:hidden">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="mr-3 rounded-md p-2.5 hover:bg-[hsl(var(--secondary))]"
          aria-label="Toggle menu"
        >
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {sidebarOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
        <Link href="/dashboard" className="flex-1 text-lg font-bold">
          OpenSkill Studio
        </Link>
        {mounted && isAuthenticated && <NotificationBell />}
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar — hidden on mobile, shown on md+ */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r bg-[hsl(var(--card))] transition-transform md:static md:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="border-b p-4">
          <Link href="/dashboard" className="text-lg font-bold">
            OpenSkill Studio
          </Link>
        </div>

        <nav className="flex-1 space-y-1 p-3">{navLinks}</nav>

        {/* Theme toggle */}
        {mounted && (
          <div className="px-3 pb-2">
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-[hsl(var(--secondary))]"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? "☀️ Light mode" : "🌙 Dark mode"}
            </button>
          </div>
        )}

        {userSection}
      </aside>

      {/* Main content */}
      <main id="main-content" className="flex-1 overflow-y-auto pt-14 md:pt-0">
        {/* Desktop header bar */}
        <div className="hidden items-center justify-end border-b px-8 py-3 md:flex">
          {mounted && isAuthenticated && <NotificationBell />}
        </div>
        <div className="p-4 md:p-8">{children}</div>
      </main>
    </div>
  );
}

function NavLink({
  href,
  children,
  active,
  onClick,
}: {
  href: string;
  children: React.ReactNode;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={cn(
        "block rounded-md px-3 py-2 text-sm",
        active
          ? "bg-[hsl(var(--secondary))] font-medium"
          : "hover:bg-[hsl(var(--secondary))]",
      )}
    >
      {children}
    </Link>
  );
}
