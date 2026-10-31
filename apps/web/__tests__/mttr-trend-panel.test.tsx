import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MttrTrendPanel } from "@/components/mttr-trend-panel";
describe("MttrTrendPanel", () => { it("renders", () => {
    const { container } = render(<MttrTrendPanel trend="improving" recentAvg={17.5} olderAvg={55} />);
    expect(container.textContent).toContain("MTTR Trend");
    expect(container.textContent).toContain("improving");
    expect(container.textContent).toContain("17.5min");
  });
});
