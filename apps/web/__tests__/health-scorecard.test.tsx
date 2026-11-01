import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthScorecard } from "@/components/health-scorecard";
describe("HealthScorecard", () => {
  it("renders", () => {
    const { container } = render(
      <HealthScorecard overall={84.8} grade="B" weakest="saturation"
        dimensions={{ availability: 99, latency: 85, errors: 95, saturation: 60 }} />
    );
    expect(container.textContent).toContain("Health Scorecard");
    expect(container.textContent).toContain("84.8");
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("availability");
    expect(container.textContent).toContain("saturation");
  });
});
