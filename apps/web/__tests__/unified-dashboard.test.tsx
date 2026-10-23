import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UnifiedDashboard } from "@/components/unified-dashboard";

describe("UnifiedDashboard", () => {
  it("renders dashboard", () => {
    const { container } = render(
      <UnifiedDashboard greeting="Good morning, Alice!" org="Acme" plan="pro"
        health={{ overall: "healthy", apps: "operational", webhooks: "good", deploys: "stable" }}
        kpis={[{ label: "Apps", value: 5, icon: "📦" }]}
        notifications={3} recentApps={[{ id: "a1", name: "SuperApp", icon: "🚀" }]}
        onNavigate={vi.fn()} />
    );
    expect(container.textContent).toContain("Good morning, Alice!");
    expect(container.textContent).toContain("Acme");
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("3");
  });
});
