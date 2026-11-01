import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperDashboard } from "@/components/developer-dashboard";

describe("DeveloperDashboard", () => {
  const quickStats = [
    { label: "Your Apps", value: 3, icon: "📦" },
    { label: "Notifications", value: 5, icon: "🔔" },
  ];
  const recentApps = [{ id: "a1", name: "SuperApp", icon: "🚀", status: "active", downloads: 5000 }];
  it("renders dashboard", () => {
    const { container } = render(
      <DeveloperDashboard greeting="Good morning, Alice!" quickStats={quickStats}
        recentApps={recentApps} hasApps={true} onSelectApp={vi.fn()} />
    );
    expect(container.textContent).toContain("Good morning, Alice!");
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("Recent Apps");
  });
});
