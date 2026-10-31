import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AvailPredictPanel } from "@/components/avail-predict-panel";
describe("AvailPredictPanel", () => {
  it("renders", () => {
    const { container } = render(
      <AvailPredictPanel trend="declining" currentPct={98} willBreach={true}
        forecast={[{ day: 1, projectedPct: 97.5 }, { day: 2, projectedPct: 97 }]} />
    );
    expect(container.textContent).toContain("Availability Prediction");
    expect(container.textContent).toContain("declining");
    expect(container.textContent).toContain("98%");
    expect(container.textContent).toContain("breach risk");
    expect(container.textContent).toContain("+1d");
    expect(container.textContent).toContain("97.5%");
  });
});
