import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CfrTrendPanel } from "@/components/cfr-trend-panel";
describe("CfrTrendPanel", () => { it("renders", () => {
    const { container } = render(<CfrTrendPanel trend="improving" recentAvg={4} olderAvg={17.5} />);
    expect(container.textContent).toContain("CFR Trend");
    expect(container.textContent).toContain("improving");
    expect(container.textContent).toContain("4%");
  });
});
