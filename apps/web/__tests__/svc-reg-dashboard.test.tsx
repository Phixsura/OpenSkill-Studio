import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcRegDashboard } from "@/components/svc-reg-dashboard";

describe("SvcRegDashboard", () => {
  it("renders", () => {
    const { container } = render(
      <SvcRegDashboard total={10} healthy={8} unhealthy={2} healthPct={80}
        byTeam={{ platform: 5, data: 3, frontend: 2 }}
        byType={{ service: 7, database: 2, cache: 1 }} />
    );
    expect(container.textContent).toContain("Service Registry");
    expect(container.textContent).toContain("10 services");
    expect(container.textContent).toContain("80% healthy");
    expect(container.textContent).toContain("platform");
    expect(container.textContent).toContain("database");
  });
});
