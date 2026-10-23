import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricAlertBadge } from "@/components/metric-alert-badge";
describe("MetricAlertBadge", () => {
  it("renders firing", () => {
    const { container } = render(<MetricAlertBadge name="CPU" value={95} threshold={80} triggered={true} status="firing" />);
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("firing");
  });
});
