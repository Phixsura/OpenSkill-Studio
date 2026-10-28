import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIAnalyticsCard from "../src/components/api-analytics-card";

const endpoints = [
  {
    method: "GET",
    path: "/api/users",
    total_requests: 5000,
    avg_latency_ms: 45,
    error_rate_pct: 1.5,
    peak_hour: 14,
  },
  {
    method: "POST",
    path: "/api/orders",
    total_requests: 2000,
    avg_latency_ms: 120,
    error_rate_pct: 5.0,
    peak_hour: 11,
  },
];

describe("APIAnalyticsCard", () => {
  it("renders header", () => {
    const { container } = render(<APIAnalyticsCard endpoints={endpoints} appName="My App" />);
    expect(container.textContent).toContain("API Analytics");
  });

  it("shows total requests", () => {
    const { container } = render(<APIAnalyticsCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("7.0K total requests");
  });

  it("renders endpoints", () => {
    const { container } = render(<APIAnalyticsCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("5.0K req");
  });

  it("shows latency and error rate", () => {
    const { container } = render(<APIAnalyticsCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("5% err");
  });

  it("shows empty state", () => {
    const { container } = render(<APIAnalyticsCard endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No analytics data");
  });
});
