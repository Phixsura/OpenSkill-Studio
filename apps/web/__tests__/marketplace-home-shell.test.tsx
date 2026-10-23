import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MarketplaceHomeShell } from "@/components/marketplace-home-shell";

describe("MarketplaceHomeShell", () => {
  it("authenticated", () => {
    const { container } = render(
      <MarketplaceHomeShell sections={[{ key: "hero", type: "banner" }]} authenticated={true}
        userName="Alice" notificationCount={3} onSearch={vi.fn()}>
        <p>Content</p>
      </MarketplaceHomeShell>
    );
    expect(container.textContent).toContain("OpenSkill Marketplace");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("(3)");
    expect(container.textContent).toContain("Content");
  });
  it("anonymous", () => {
    const { container } = render(
      <MarketplaceHomeShell sections={[]} authenticated={false} onSearch={vi.fn()}>
        <p>C</p>
      </MarketplaceHomeShell>
    );
    expect(container.textContent).toContain("Sign In");
  });
});
