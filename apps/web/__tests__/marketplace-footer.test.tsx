import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceFooter } from "@/components/marketplace-footer";

describe("MarketplaceFooter", () => {
  it("shows sections", () => {
    const { container } = render(<MarketplaceFooter sections={{ Browse: [{ label: "Apps", url: "/" }] }} copyright="© 2026" />);
    expect(container.textContent).toContain("Browse");
    expect(container.textContent).toContain("Apps");
  });
  it("shows copyright", () => {
    const { container } = render(<MarketplaceFooter sections={{}} copyright="© 2026 OpenSkill" />);
    expect(container.textContent).toContain("© 2026");
  });
});
