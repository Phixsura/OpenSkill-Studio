import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthPredictPanel } from "@/components/health-predict-panel";
describe("HealthPredictPanel", () => {
  it("renders", () => {
    const { container } = render(
      <HealthPredictPanel trend="declining" current={98} willBreachSla={true}
        forecast={[{ period: 1, projected: 97.5 }, { period: 2, projected: 97 }]} />
    );
    expect(container.textContent).toContain("Health Prediction");
    expect(container.textContent).toContain("declining");
    expect(container.textContent).toContain("98%");
    expect(container.textContent).toContain("SLA at risk");
    expect(container.textContent).toContain("+1d");
    expect(container.textContent).toContain("97.5%");
  });
});
