import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcStatusAggPanel } from "@/components/svc-status-agg-panel";
describe("SvcStatusAggPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SvcStatusAggPanel healthy={1} unhealthy={1}
        services={[
          { service: "api", consensus: "healthy", reports: 2 },
          { service: "db", consensus: "down", reports: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Service Status");
    expect(container.textContent).toContain("1 healthy");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("down");
  });
});
