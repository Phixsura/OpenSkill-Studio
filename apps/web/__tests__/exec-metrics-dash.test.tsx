import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExecMetricsDash } from "@/components/exec-metrics-dash";

describe("ExecMetricsDash", () => {
  it("renders", () => {
    const { container } = render(
      <ExecMetricsDash health="green" uptimePct={99.99} errorRatePct={0.05}
        p99Ms={80} dailyUsers={5000} dailyApiCalls={100000} />
    );
    expect(container.textContent).toContain("GREEN");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("0.05%");
    expect(container.textContent).toContain("80ms");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("100,000");
  });
});
