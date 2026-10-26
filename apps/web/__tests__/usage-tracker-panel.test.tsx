import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageTrackerPanel } from "@/components/usage-tracker-panel";

const props = {
  peaks: { cpu: 92, memoryMb: 450, networkBytes: 52428800, apiCalls: 500 },
  averages: { cpu: 55, memoryMb: 280, apiCalls: 150 },
  forecast: { forecast: 9000, confidence: "high" as const },
  totalApiCalls: 45000,
  totalNetworkBytes: 524288000,
  windowMinutes: 60,
};

describe("UsageTrackerPanel", () => {
  it("renders peaks", () => {
    const { container } = render(<UsageTrackerPanel {...props} />);
    expect(container.textContent).toContain("92%");
    expect(container.textContent).toContain("450MB");
    expect(container.textContent).toContain("500");
  });

  it("renders averages", () => {
    const { container } = render(<UsageTrackerPanel {...props} />);
    expect(container.textContent).toContain("55%");
    expect(container.textContent).toContain("280MB");
  });

  it("shows forecast with confidence", () => {
    const { container } = render(<UsageTrackerPanel {...props} />);
    expect(container.textContent).toContain("9000");
    expect(container.textContent).toContain("high");
  });

  it("shows totals", () => {
    const { container } = render(<UsageTrackerPanel {...props} />);
    expect(container.textContent).toContain("45,000");
    expect(container.textContent).toContain("Last 60min");
  });
});
