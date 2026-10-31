import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateAnalyzePanel } from "@/components/rate-analyze-panel";
describe("RateAnalyzePanel", () => {
  it("renders", () => {
    const { container } = render(
      <RateAnalyzePanel rps={150} total={10000} avgPerWindow={50}
        maxPerWindow={200} spikeDetected={true} />
    );
    expect(container.textContent).toContain("Request Rate");
    expect(container.textContent).toContain("150 rps");
    expect(container.textContent).toContain("SPIKE");
    expect(container.textContent).toContain("10,000 total");
    expect(container.textContent).toContain("200");
  });
});
