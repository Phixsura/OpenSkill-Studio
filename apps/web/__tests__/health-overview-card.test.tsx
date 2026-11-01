import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthOverviewCard } from "@/components/health-overview-card";

describe("HealthOverviewCard", () => {
  it("shows avg score", () => {
    const { container } = render(<HealthOverviewCard total={3} healthy={1} degraded={1} critical={1} avgScore={81} worstApp={{ name: "Bad", score: 60 }} />);
    expect(container.textContent).toContain("81%");
  });
  it("shows worst app", () => {
    const { container } = render(<HealthOverviewCard total={2} healthy={1} degraded={0} critical={1} avgScore={80} worstApp={{ name: "Broken", score: 40 }} />);
    expect(container.textContent).toContain("Broken");
    expect(container.textContent).toContain("40%");
  });
});
