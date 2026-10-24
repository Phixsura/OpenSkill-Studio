import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthcheckEndpoint } from "@/components/healthcheck-endpoint";

describe("HealthcheckEndpoint", () => {
  it("renders health", () => {
    const { container } = render(
      <HealthcheckEndpoint status="pass" ready={true} notReadyDeps={[]} output="All systems operational"
        checks={{
          database: { status: "up", latencyMs: 5, message: "" },
          cache: { status: "up", latencyMs: 1, message: "" },
        }} />
    );
    expect(container.textContent).toContain("Health Check");
    expect(container.textContent).toContain("pass");
    expect(container.textContent).toContain("ready");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("5ms");
    expect(container.textContent).toContain("All systems operational");
  });
});
