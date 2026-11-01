import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LoadTestPanel } from "@/components/load-test-panel";

describe("LoadTestPanel", () => {
  it("renders", () => {
    const { container } = render(
      <LoadTestPanel rps={166.7} totalRequests={10000} errorRatePct={0.05}
        p50Ms={20} p95Ms={80} p99Ms={150} passed={true} />
    );
    expect(container.textContent).toContain("Load Test");
    expect(container.textContent).toContain("PASSED");
    expect(container.textContent).toContain("166.7 rps");
    expect(container.textContent).toContain("20ms");
    expect(container.textContent).toContain("150ms");
    expect(container.textContent).toContain("10,000 requests");
  });
});
