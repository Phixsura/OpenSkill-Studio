import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone2700Banner } from "@/components/milestone-2700-banner";

describe("Milestone2700Banner", () => {
  it("renders", () => {
    const { container } = render(<Milestone2700Banner />);
    expect(container.textContent).toContain("2,700 Commits");
    expect(container.textContent).toContain("233K+");
    expect(container.textContent).toContain("7,912+");
    expect(container.textContent).toContain("All Systems Green");
    expect(container.textContent).toContain("1,350+");
  });
});
