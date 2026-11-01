import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TeamPerfCard } from "@/components/team-perf-card";

describe("TeamPerfCard", () => {
  it("renders", () => {
    const { container } = render(
      <TeamPerfCard team="Platform" healthScore={88} rating="excellent"
        velocity={60} cycleTimeDays={3} deploysPerWeek={8} incidents={0} prReviewHours={4} />
    );
    expect(container.textContent).toContain("Platform");
    expect(container.textContent).toContain("88");
    expect(container.textContent).toContain("excellent");
    expect(container.textContent).toContain("60");
    expect(container.textContent).toContain("3d");
    expect(container.textContent).toContain("4h");
  });
});
