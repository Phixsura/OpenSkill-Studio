import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiRateDashboard } from "@/components/api-rate-dashboard";

describe("ApiRateDashboard", () => {
  const endpoints = [
    { path: "/api/users", method: "GET", currentRpm: 150, rpmLimit: 100, usagePct: 150, throttled: true },
    { path: "/api/apps", method: "GET", currentRpm: 80, rpmLimit: 100, usagePct: 80, throttled: false },
  ];
  it("renders rate limits", () => {
    const { container } = render(
      <ApiRateDashboard endpoints={endpoints} totalRpm={230} throttledCount={1} healthy={false} />
    );
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("150/100");
    expect(container.textContent).toContain("1 throttled");
  });
});
