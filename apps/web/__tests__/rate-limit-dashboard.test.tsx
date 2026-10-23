import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RateLimitDashboard } from "@/components/rate-limit-dashboard";

describe("RateLimitDashboard", () => {
  it("renders endpoints", () => {
    const endpoints = [{ path: "/users", limit: 100, current: 80 }, { path: "/apps", limit: 200, current: 50 }];
    const { container } = render(<RateLimitDashboard endpoints={endpoints} totalUsagePct={43} hotspotCount={1} />);
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("80/100");
    expect(container.textContent).toContain("1 hotspot");
  });
});
