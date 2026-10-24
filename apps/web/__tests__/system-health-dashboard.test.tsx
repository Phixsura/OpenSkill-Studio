import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SystemHealthDashboard } from "@/components/system-health-dashboard";

describe("SystemHealthDashboard", () => {
  it("renders health", () => {
    const { container } = render(
      <SystemHealthDashboard overall="degraded" healthDisplay="67%" healthy={2} total={3}
        checks={[
          { name: "API", status: "healthy", latencyMs: 25, message: "" },
          { name: "Database", status: "healthy", latencyMs: 5, message: "" },
          { name: "Cache", status: "unhealthy", latencyMs: 0, message: "Connection refused" },
        ]} />
    );
    expect(container.textContent).toContain("System Health");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("Connection refused");
    expect(container.textContent).toContain("2/3");
  });
});
