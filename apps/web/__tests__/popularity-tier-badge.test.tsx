import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PopularityTierBadge } from "@/components/popularity-tier-badge";

describe("PopularityTierBadge", () => {
  it("renders badge", () => {
    const { container } = render(<PopularityTierBadge tier="gold" score={35} rank={1} />);
    expect(container.textContent).toContain("Gold");
    expect(container.textContent).toContain("#1");
  });
});
