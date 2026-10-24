import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthProbeStatus } from "@/components/health-probe-status";

describe("HealthProbeStatus", () => {
  it("renders", () => {
    const { container } = render(
      <HealthProbeStatus liveness="ok" readiness="not_ready" startup="complete"
        failedChecks={["cache"]} />
    );
    expect(container.textContent).toContain("Health Probes");
    expect(container.textContent).toContain("ok");
    expect(container.textContent).toContain("not_ready");
    expect(container.textContent).toContain("complete");
    expect(container.textContent).toContain("Failed: cache");
  });
});
