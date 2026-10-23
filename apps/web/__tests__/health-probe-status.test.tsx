import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthProbeStatus } from "@/components/health-probe-status";

describe("HealthProbeStatus", () => {
  it("renders probe", () => {
    const { container } = render(
      <HealthProbeStatus ready={false} status="not_ready" dependencies={[
        { name: "database", ready: true, latencyMs: 5 },
        { name: "cache", ready: false, latencyMs: 0 },
      ]} />
    );
    expect(container.textContent).toContain("not_ready");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("cache");
    expect(container.textContent).toContain("5ms");
  });
});
