import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceFooter } from "@/components/marketplace-footer";
describe("MarketplaceFooter", () => {
  it("renders", () => {
    const { container } = render(<MarketplaceFooter version="3.0" year={2026} />);
    expect(container.textContent).toContain("v3.0");
    expect(container.textContent).toContain("2026");
  });
});
