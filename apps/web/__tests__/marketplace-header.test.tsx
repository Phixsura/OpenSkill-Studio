import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceHeader } from "@/components/marketplace-header";

describe("MarketplaceHeader", () => {
  const nav = [{ label: "Explore", href: "/marketplace", icon: "🏪", active: true }];
  it("renders logged in", () => {
    const { container } = render(
      <MarketplaceHeader nav={nav} user={{ name: "Alice", initials: "AC", plan: "pro" }}
        notifications={5} loggedIn={true} onNavigate={vi.fn()} onSearch={vi.fn()} />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("Explore");
    expect(container.textContent).toContain("AC");
    expect(container.textContent).toContain("5");
  });
  it("renders logged out", () => {
    const { container } = render(
      <MarketplaceHeader nav={nav} user={null} notifications={0} loggedIn={false}
        onNavigate={vi.fn()} onSearch={vi.fn()} />
    );
    expect(container.textContent).toContain("Sign In");
  });
});
