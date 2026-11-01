import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceHero } from "@/components/marketplace-hero";
describe("MarketplaceHero", () => {
  it("renders", () => {
    const { container } = render(<MarketplaceHero title="Marketplace" subtitle="Build anything" extensionCount={500} />);
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("500");
  });
});
