import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone2900 } from "@/components/milestone-2900";

describe("Milestone2900", () => {
  it("renders", () => {
    const { container } = render(<Milestone2900 />);
    expect(container.textContent).toContain("2,900 Commits");
    expect(container.textContent).toContain("249K Lines");
    expect(container.textContent).toContain("250,000 LINES");
  });
});
