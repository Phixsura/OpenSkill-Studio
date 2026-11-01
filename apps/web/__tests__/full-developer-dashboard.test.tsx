import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FullDeveloperDashboard } from "@/components/full-developer-dashboard";

describe("FullDeveloperDashboard", () => {
  const props = {
    developer: { name: "Alice", verified: true, plan: "pro" },
    overview: { total_apps: 5, active_apps: 4, total_installs: 8000,
      total_revenue: 4000, avg_rating: 4.5, notifications: 3 },
    topApp: { name: "Auth SDK", installs: 5000 },
    analytics: { dau: 500, wau: 2000, mau: 5000, api_calls_today: 15000, error_rate: 0.1 },
    quickActions: [{ id: "new", label: "Create", icon: "➕" }],
  };
  it("renders", () => {
    const { container } = render(<FullDeveloperDashboard {...props} onAction={vi.fn()} />);
    expect(container.textContent).toContain("Welcome, Alice!");
    expect(container.textContent).toContain("✓ Verified");
    expect(container.textContent).toContain("pro plan");
    expect(container.textContent).toContain("8,000");
    expect(container.textContent).toContain("$4,000");
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("🔔 3");
  });
});
