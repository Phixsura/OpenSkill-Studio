import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppHomePage } from "@/components/app-home-page";

describe("AppHomePage", () => {
  it("renders app home", () => {
    const { container } = render(
      <AppHomePage header={{ name: "SuperApp", icon: "🚀", version: "2.0.0", status: "active", published: true }}
        quickStats={[{ label: "Installs", value: 25000, icon: "📥", display: "25,000" }]}
        recentActivity={[{ action: "Deployed v2.0.0", timestamp: "2026-10-01" }]}
        hasUpdate={true} quickLinks={[{ label: "Analytics", href: "analytics", icon: "📊" }]}
        onNavigate={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("25,000");
    expect(container.textContent).toContain("Update available");
    expect(container.textContent).toContain("Analytics");
    expect(container.textContent).toContain("Deployed v2.0.0");
  });
});
