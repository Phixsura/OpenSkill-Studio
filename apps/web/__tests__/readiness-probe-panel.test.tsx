import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReadinessProbePanel } from "@/components/readiness-probe-panel";

describe("ReadinessProbePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReadinessProbePanel ready={1} total={2} allReady={false}
        services={[
          { service: "api", ready: true, checks: { database: true, cache: true, config: true } },
          { service: "worker", ready: false, checks: { database: true, cache: true, config: false } },
        ]} />
    );
    expect(container.textContent).toContain("Readiness Probes");
    expect(container.textContent).toContain("1/2 ready");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("worker");
    expect(container.textContent).toContain("✗ config");
  });
});
