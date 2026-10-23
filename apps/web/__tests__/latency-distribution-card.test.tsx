import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatencyDistributionCard } from "@/components/latency-distribution-card";

describe("LatencyDistributionCard", () => {
  it("renders percentiles", () => {
    const { container } = render(<LatencyDistributionCard p50={50} p90={150} p95={200} p99={400} avg={80} />);
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("400");
    expect(container.textContent).toContain("P99");
  });
  it("shows target", () => {
    const { container } = render(<LatencyDistributionCard p50={50} p90={100} p95={150} p99={200} avg={60} targetP99={500} />);
    expect(container.textContent).toContain("Target: 500ms");
    expect(container.textContent).toContain("✅");
  });
  it("shows exceeded", () => {
    const { container } = render(<LatencyDistributionCard p50={50} p90={100} p95={300} p99={600} avg={80} targetP99={500} />);
    expect(container.textContent).toContain("⚠️");
  });
});
