import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FinalOpsHero } from "@/components/final-ops-hero";

describe("FinalOpsHero", () => {
  it("renders", () => {
    const { container } = render(<FinalOpsHero />);
    expect(container.textContent).toContain("8,000 FILES");
    expect(container.textContent).toContain("235K+");
    expect(container.textContent).toContain("2,725");
    expect(container.textContent).toContain("All Systems Green");
  });
});
