import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3000 } from "@/components/milestone-3000";
describe("Milestone3000", () => {
  it("renders", () => {
    const { container } = render(<Milestone3000 />);
    expect(container.textContent).toContain("THREE THOUSAND");
    expect(container.textContent).toContain("3,000 Commits");
    expect(container.textContent).toContain("All Operational");
  });
});
