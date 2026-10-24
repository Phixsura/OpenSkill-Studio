import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrAnomalyPanel } from "@/components/err-anomaly-panel";
describe("ErrAnomalyPanel", () => {
  it("renders anomaly", () => {
    const { container } = render(
      <ErrAnomalyPanel anomaly={true} latest={5} mean={0.1} zScore={3.2} trend="worsening" />
    );
    expect(container.textContent).toContain("Error Anomaly");
    expect(container.textContent).toContain("ANOMALY");
    expect(container.textContent).toContain("3.2σ");
    expect(container.textContent).toContain("5%");
    expect(container.textContent).toContain("0.1%");
    expect(container.textContent).toContain("worsening");
  });
});
