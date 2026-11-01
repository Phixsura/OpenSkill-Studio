import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LoadTestReport } from "@/components/load-test-report";

describe("LoadTestReport", () => {
  it("renders report", () => {
    const { container } = render(
      <LoadTestReport endpoint="/api/users" rps={100} durationSec={60}
        totalRequests={6000} successful={5970} failed={30}
        avgLatencyMs={85} errorRatePct={0.5} passed={true} regression={false} />
    );
    expect(container.textContent).toContain("Load Test");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("Passed");
    expect(container.textContent).toContain("6,000");
    expect(container.textContent).toContain("85ms");
    expect(container.textContent).toContain("0.5%");
    expect(container.textContent).toContain("Improved");
  });
});
