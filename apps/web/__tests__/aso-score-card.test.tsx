import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AsoScoreCard } from "@/components/aso-score-card";

describe("AsoScoreCard", () => {
  it("renders score", () => {
    const { container } = render(<AsoScoreCard score={75} grade="B" suggestions={["Add icon"]} />);
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("75/100");
    expect(container.textContent).toContain("Add icon");
  });
  it("perfect listing", () => {
    const { container } = render(<AsoScoreCard score={100} grade="A" suggestions={[]} />);
    expect(container.textContent).toContain("Perfect listing");
  });
});
