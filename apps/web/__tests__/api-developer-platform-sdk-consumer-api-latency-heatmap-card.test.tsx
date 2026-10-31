import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LatencyHeatmapCard from "../src/components/api-developer-platform-sdk-consumer-api-latency-heatmap-card";

describe("LatencyHeatmapCard", () => {
  it("renders title and endpoints", () => {
    const { container } = render(<LatencyHeatmapCard />);
    expect(container.textContent).toContain("Latency Heatmap");
    expect(container.textContent).toContain("ep-auth");
    expect(container.textContent).toContain("ep-search");
  });

  it("shows percentiles", () => {
    const { container } = render(<LatencyHeatmapCard />);
    expect(container.textContent).toContain("P50:");
    expect(container.textContent).toContain("P95:");
    expect(container.textContent).toContain("P99:");
    expect(container.textContent).toContain("3 endpoints tracked");
  });
});
