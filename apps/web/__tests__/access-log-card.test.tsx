import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AccessLogCard from "../src/components/access-log-card";

const endpoints = [
  {
    method: "GET",
    path: "/api/users",
    total_requests: 1500,
    error_count: 15,
    avg_response_ms: 45,
    p95_response_ms: 120,
    error_rate_pct: 1.0,
  },
  {
    method: "POST",
    path: "/api/users",
    total_requests: 300,
    error_count: 30,
    avg_response_ms: 150,
    p95_response_ms: 500,
    error_rate_pct: 10.0,
  },
];

describe("AccessLogCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <AccessLogCard
        endpoints={endpoints}
        appName="My App"
        overallErrorRate={2.5}
        totalRequests={1800}
      />,
    );
    expect(container.textContent).toContain("Access Log");
    expect(container.textContent).toContain("My App");
  });

  it("shows total requests", () => {
    const { container } = render(
      <AccessLogCard
        endpoints={endpoints}
        appName="App"
        overallErrorRate={2.5}
        totalRequests={1800}
      />,
    );
    expect(container.textContent).toContain("1.8K requests");
  });

  it("shows overall error rate", () => {
    const { container } = render(
      <AccessLogCard
        endpoints={endpoints}
        appName="App"
        overallErrorRate={2.5}
        totalRequests={1800}
      />,
    );
    expect(container.textContent).toContain("2.5% errors");
  });

  it("renders method badges", () => {
    const { container } = render(
      <AccessLogCard endpoints={endpoints} appName="App" overallErrorRate={0} totalRequests={0} />,
    );
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("POST");
  });

  it("renders paths", () => {
    const { container } = render(
      <AccessLogCard endpoints={endpoints} appName="App" overallErrorRate={0} totalRequests={0} />,
    );
    expect(container.textContent).toContain("/api/users");
  });

  it("shows response time stats", () => {
    const { container } = render(
      <AccessLogCard endpoints={endpoints} appName="App" overallErrorRate={0} totalRequests={0} />,
    );
    expect(container.textContent).toContain("avg 45ms");
    expect(container.textContent).toContain("p95 120ms");
  });

  it("shows endpoint error rate", () => {
    const { container } = render(
      <AccessLogCard endpoints={endpoints} appName="App" overallErrorRate={0} totalRequests={0} />,
    );
    expect(container.textContent).toContain("10.0% err");
  });

  it("shows empty state", () => {
    const { container } = render(
      <AccessLogCard endpoints={[]} appName="App" overallErrorRate={0} totalRequests={0} />,
    );
    expect(container.textContent).toContain("No endpoints tracked");
  });
});
