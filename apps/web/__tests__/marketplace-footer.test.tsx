import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceFooter } from "@/components/marketplace-footer";

describe("MarketplaceFooter", () => {
  const sections = { Marketplace: [{ label: "Browse", href: "/marketplace" }] };
  const social = [{ name: "GitHub", href: "https://github.com", icon: "🐙" }];
  it("renders footer", () => {
    const { container } = render(
      <MarketplaceFooter sections={sections} copyright="© 2026 OpenSkill" social={social} />
    );
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("Browse");
    expect(container.textContent).toContain("© 2026 OpenSkill");
    expect(container.textContent).toContain("🐙");
  });
});
