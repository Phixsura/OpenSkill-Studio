import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone239k } from "@/components/milestone-239k";

describe("Milestone239k", () => {
  it("renders", () => {
    const { container } = render(<Milestone239k />);
    expect(container.textContent).toContain("239K+");
    expect(container.textContent).toContain("2,774");
    expect(container.textContent).toContain("All Systems Green");
  });
});
