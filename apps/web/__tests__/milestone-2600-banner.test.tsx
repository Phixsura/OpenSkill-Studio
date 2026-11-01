import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone2600Banner } from "@/components/milestone-2600-banner";

describe("Milestone2600Banner", () => {
  it("renders milestone", () => {
    const { container } = render(<Milestone2600Banner />);
    expect(container.textContent).toContain("2,600 Commits");
    expect(container.textContent).toContain("224K Lines");
    expect(container.textContent).toContain("7,550+");
    expect(container.textContent).toContain("1,300+");
    expect(container.textContent).toContain("Fully Operational");
  });
});
