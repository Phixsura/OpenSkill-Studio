import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GatewayRlOverview } from "@/components/gateway-rl-overview";

describe("GatewayRlOverview", () => {
  it("renders overview", () => {
    const { container } = render(
      <GatewayRlOverview totalRequests={1230} totalBlocked={50} blockRateDisplay="3.9%"
        exceededCount={1} routes={[
          { path: "/api/v1/users", method: "GET", requests: 950, blocked: 50, limit: 1000, usagePct: 95, status: "exceeded" },
          { path: "/api/v1/apps", method: "GET", requests: 200, blocked: 0, limit: 500, usagePct: 40, status: "ok" },
        ]} />
    );
    expect(container.textContent).toContain("Rate Limits Overview");
    expect(container.textContent).toContain("1,230 requests");
    expect(container.textContent).toContain("50 blocked");
    expect(container.textContent).toContain("1 exceeded");
    expect(container.textContent).toContain("/api/v1/users");
  });
});
