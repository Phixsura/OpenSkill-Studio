"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, clearAuth } = useAuthStore();

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

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col border-r bg-[hsl(var(--card))]">
        <div className="border-b p-4">
          <Link href="/dashboard" className="text-lg font-bold">
            OpenSkill Studio
          </Link>
        </div>

        <nav className="flex-1 space-y-1 p-3">
          <NavLink href="/dashboard" active={pathname === "/dashboard"}>Dashboard</NavLink>
          <NavLink href="/dashboard/orgs" active={pathname.startsWith("/dashboard/orgs")}>Organizations</NavLink>
          <NavLink href="/dashboard/skills" active={pathname === "/dashboard/skills"}>Skills</NavLink>
          <NavLink href="/dashboard/projects" active={pathname === "/dashboard/projects"}>Projects</NavLink>
          <NavLink href="/dashboard/portfolio" active={pathname.startsWith("/dashboard/portfolio")}>Portfolio</NavLink>
          <NavLink href="/dashboard/settings" active={pathname === "/dashboard/settings"}>Settings</NavLink>
        </nav>

        {/* User section */}
        <div className="border-t p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[hsl(var(--primary))] text-sm font-medium text-[hsl(var(--primary-foreground))]">
              {user?.display_name?.charAt(0)?.toUpperCase() ?? "?"}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">
                {user?.display_name ?? "User"}
              </p>
              <p className="truncate text-xs text-[hsl(var(--muted-foreground))]">
                {user?.email}
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
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto p-8">{children}</main>
    </div>
  );
}

function NavLink({
  href,
  children,
  active,
}: {
  href: string;
  children: React.ReactNode;
  active?: boolean;
}) {
  return (
    <Link
      href={href}
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
