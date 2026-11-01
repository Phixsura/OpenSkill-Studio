import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CompleteNavLayout } from "@/components/complete-nav-layout";

describe("CompleteNavLayout", () => {
  const mainNav = [{ id: "marketplace", label: "Marketplace", href: "/marketplace", icon: "🏪", active: true }];
  const consoleNav = [{ id: "dashboard", label: "Dashboard", href: "/console", icon: "📊", active: true }];
  const footerNav = { Product: [{ label: "Marketplace", href: "/marketplace" }] };
  it("renders layout", () => {
    const { container } = render(
      <CompleteNavLayout mainNav={mainNav} consoleNav={consoleNav} footerNav={footerNav}
        showConsole={true} onNavigate={vi.fn()}>
        <p>Page content</p>
      </CompleteNavLayout>
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("Dashboard");
    expect(container.textContent).toContain("Page content");
  });
});
