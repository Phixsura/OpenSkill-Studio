import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone230kBanner } from "@/components/milestone-230k-banner";

describe("Milestone230kBanner", () => {
  it("renders", () => {
    const { container } = render(<Milestone230kBanner />);
    expect(container.textContent).toContain("230K Lines");
    expect(container.textContent).toContain("2,666+");
    expect(container.textContent).toContain("7,784+");
    expect(container.textContent).toContain("Fully Operational");
  });
});
