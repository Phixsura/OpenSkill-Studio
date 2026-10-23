import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CompleteMarketplaceAppShell } from "@/components/complete-marketplace-app-shell";

describe("CompleteMarketplaceAppShell", () => {
  const nav = [{ label: "Explore", url: "/marketplace", icon: "🏪" }];
  it("authenticated", () => {
    const { container } = render(
      <CompleteMarketplaceAppShell platformName="OpenSkill" authenticated={true} userName="Alice"
        notificationCount={3} theme="light" navItems={nav}>
        <p>Page content</p>
      </CompleteMarketplaceAppShell>
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("Page content");
    expect(container.textContent).toContain("© 2026");
  });
  it("anonymous", () => {
    const { container } = render(
      <CompleteMarketplaceAppShell platformName="OpenSkill" authenticated={false}
        notificationCount={0} theme="system" navItems={nav}>
        <p>Content</p>
      </CompleteMarketplaceAppShell>
    );
    expect(container.textContent).toContain("Sign In");
  });
});
