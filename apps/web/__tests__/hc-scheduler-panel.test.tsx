import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HcSchedulerPanel } from "@/components/hc-scheduler-panel";
describe("HcSchedulerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <HcSchedulerPanel healthy={1} unhealthy={1}
        checks={[
          { name: "api", status: "healthy", interval: 30, consecutiveFailures: 0 },
          { name: "db", status: "unhealthy", interval: 60, consecutiveFailures: 3 },
        ]} />
    );
    expect(container.textContent).toContain("Health Check Scheduler");
    expect(container.textContent).toContain("1 healthy");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("every 30s");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("3 fails");
  });
});
