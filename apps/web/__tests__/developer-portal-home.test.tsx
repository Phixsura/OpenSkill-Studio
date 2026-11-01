import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperPortalHome } from "@/components/developer-portal-home";

describe("DeveloperPortalHome", () => {
  const stats = { apps: 5, installs: 8000, revenue: 4000, avg_rating: 4.5 };
  const recentApps = [{ id: "a1", name: "Auth SDK", installs: 5000 }];
  const quickLinks = [{ label: "Create App", icon: "➕", url: "/apps/new" }];
  it("renders", () => {
    const { container } = render(
      <DeveloperPortalHome greeting="Welcome, Alice!" stats={stats} recentApps={recentApps}
        notifications={3} quickLinks={quickLinks} onNavigate={vi.fn()} />
    );
    expect(container.textContent).toContain("Welcome, Alice!");
    expect(container.textContent).toContain("🔔 3");
    expect(container.textContent).toContain("8,000");
    expect(container.textContent).toContain("$4,000");
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("Create App");
  });
});
