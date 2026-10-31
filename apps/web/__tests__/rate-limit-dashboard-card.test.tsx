import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RateLimitDashboardCard from "../src/components/rate-limit-dashboard-card";

const okLimit = {
  key: "api/v1/users",
  count: 30,
  limit: 100,
  remaining: 70,
  window_seconds: 60,
  reset_in_seconds: 45,
  blocked: false,
};

const blockedLimit = {
  key: "api/v1/search",
  count: 50,
  limit: 50,
  remaining: 0,
  window_seconds: 60,
  reset_in_seconds: 12,
  blocked: true,
};

describe("RateLimitDashboardCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<RateLimitDashboardCard limits={[okLimit]} appName="My App" />);
    expect(container.textContent).toContain("Rate Limits");
    expect(container.textContent).toContain("My App");
  });

  it("shows all-clear when nothing blocked", () => {
    const { container } = render(<RateLimitDashboardCard limits={[okLimit]} appName="App" />);
    expect(container.textContent).toContain("All clear");
  });

  it("shows throttled count", () => {
    const { container } = render(
      <RateLimitDashboardCard limits={[okLimit, blockedLimit]} appName="App" />,
    );
    expect(container.textContent).toContain("1 throttled");
  });

  it("renders key and window", () => {
    const { container } = render(<RateLimitDashboardCard limits={[okLimit]} appName="App" />);
    expect(container.textContent).toContain("api/v1/users");
    expect(container.textContent).toContain("60s window");
  });

  it("shows request count", () => {
    const { container } = render(<RateLimitDashboardCard limits={[okLimit]} appName="App" />);
    expect(container.textContent).toContain("30 / 100 requests");
    expect(container.textContent).toContain("70 remaining");
  });

  it("shows reset time for blocked", () => {
    const { container } = render(<RateLimitDashboardCard limits={[blockedLimit]} appName="App" />);
    expect(container.textContent).toContain("Resets in 12s");
  });

  it("shows empty state", () => {
    const { container } = render(<RateLimitDashboardCard limits={[]} appName="App" />);
    expect(container.textContent).toContain("No rate limits tracked");
  });
});
