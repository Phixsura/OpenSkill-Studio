import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplacePageLayout } from "@/components/marketplace-page-layout";

describe("MarketplacePageLayout", () => {
  it("shows header", () => {
    const { container } = render(<MarketplacePageLayout activePage="home"><p>Content</p></MarketplacePageLayout>);
    expect(container.textContent).toContain("OpenSkill Marketplace");
    expect(container.textContent).toContain("Content");
  });
  it("shows footer", () => {
    const { container } = render(<MarketplacePageLayout activePage=""><div /></MarketplacePageLayout>);
    expect(container.textContent).toContain("© 2026");
  });
});
