import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UptimeTrendPanel } from "@/components/uptime-trend-panel";
describe("UptimeTrendPanel", () => {
  it("renders", () => {
    const { container } = render(<UptimeTrendPanel trend="improving" recent={99.8} older={99.2} current={99.99} />);
    expect(container.textContent).toContain("Uptime Trend");
    expect(container.textContent).toContain("improving");
    expect(container.textContent).toContain("99.99%");
  });
});
