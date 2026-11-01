import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CapacityPlannerCard } from "@/components/capacity-planner-card";

describe("CapacityPlannerCard", () => {
  it("renders planner", () => {
    const forecasts = [{ month: 1, projected: 55000 }, { month: 2, projected: 60500 }, { month: 3, projected: 66550 }];
    const { container } = render(
      <CapacityPlannerCard currentUsage={50000} forecasts={forecasts} recommendedPlan="pro" shouldScale={false} />
    );
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("55,000");
    expect(container.textContent).toContain("pro");
  });
  it("shows scale warning", () => {
    const { container } = render(
      <CapacityPlannerCard currentUsage={95000} forecasts={[]} recommendedPlan="enterprise" shouldScale={true} />
    );
    expect(container.textContent).toContain("Scale recommended");
  });
});
