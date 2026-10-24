import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone2650 } from "@/components/milestone-2650";

describe("Milestone2650", () => {
  it("renders", () => {
    const { container } = render(<Milestone2650 />);
    expect(container.textContent).toContain("2,650 Commits");
    expect(container.textContent).toContain("228K+");
    expect(container.textContent).toContain("Fully Operational");
  });
});
