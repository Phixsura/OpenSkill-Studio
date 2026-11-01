import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CompleteDashboard } from "@/components/complete-dashboard";

describe("CompleteDashboard", () => {
  it("renders complete dashboard", () => {
    const { container } = render(
      <CompleteDashboard greeting="Good morning, Alice!"
        orgName="Acme Corp" orgPlan="pro"
        quickStats={[{ label: "Apps", value: 5, icon: "📦" }, { label: "Installs", value: 30000, display: "30,000", icon: "📥" }]}
        recentApps={[{ id: "a1", name: "SuperApp", icon: "🚀", status: "active" }]}
        quickActions={[{ label: "Create App", href: "/new", icon: "➕" }]}
        topApp={{ name: "SuperApp", icon: "🚀", installs: 25000 }}
        onNavigate={vi.fn()} onSelectApp={vi.fn()} />
    );
    expect(container.textContent).toContain("Good morning, Alice!");
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("30,000");
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("Top App");
    expect(container.textContent).toContain("Create App");
  });
});
