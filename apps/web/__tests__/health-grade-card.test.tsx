import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthGradeCard } from "@/components/health-grade-card";

describe("HealthGradeCard", () => {
  it("shows grade", () => {
    const { container } = render(<HealthGradeCard grade="A" score={96} month="Oct 2026" />);
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("96%");
  });
  it("shows month", () => {
    const { container } = render(<HealthGradeCard grade="B" score={88} month="Sep 2026" />);
    expect(container.textContent).toContain("Sep 2026");
  });
});
