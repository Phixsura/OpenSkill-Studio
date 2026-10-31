import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone250K } from "@/components/milestone-250k";

describe("Milestone250K", () => {
  it("renders celebration", () => {
    const { container } = render(<Milestone250K />);
    expect(container.textContent).toContain("QUARTER MILLION");
    expect(container.textContent).toContain("250,000");
    expect(container.textContent).toContain("2,906+");
    expect(container.textContent).toContain("8,640+");
    expect(container.textContent).toContain("Extension SDK");
    expect(container.textContent).toContain("All Operational");
  });
});
