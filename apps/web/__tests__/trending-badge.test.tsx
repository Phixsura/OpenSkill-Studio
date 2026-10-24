import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TrendingBadge } from "@/components/trending-badge";

describe("TrendingBadge", () => {
  it("shows rank and score", () => {
    const { container } = render(<TrendingBadge rank={1} score={150} />);
    expect(container.textContent).toContain("#1");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("🔥");
  });
});
