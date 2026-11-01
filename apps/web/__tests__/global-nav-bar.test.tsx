import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GlobalNavBar } from "@/components/global-nav-bar";

describe("GlobalNavBar", () => {
  it("renders nav", () => {
    const { container } = render(
      <GlobalNavBar onNavigate={vi.fn()} sections={[
        { id: "marketplace", label: "Marketplace", icon: "🏪", active: false,
          items: [{ label: "Browse", path: "/marketplace", icon: "📱" }] },
        { id: "develop", label: "Develop", icon: "💻", active: true,
          items: [{ label: "Dashboard", path: "/dashboard", icon: "🏠" }] },
      ]} />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("Develop");
    expect(container.textContent).toContain("Browse");
    expect(container.textContent).toContain("Dashboard");
  });
});
