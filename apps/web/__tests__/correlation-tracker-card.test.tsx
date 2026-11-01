import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CorrelationTrackerCard from "../src/components/correlation-tracker-card";

const spans = [
  {
    span_id: "s1",
    service: "api-gw",
    operation: "GET /users",
    status: "ok" as const,
    duration_ms: 150,
    parent_span_id: null,
    depth: 0,
  },
  {
    span_id: "s2",
    service: "user-svc",
    operation: "findAll",
    status: "ok" as const,
    duration_ms: 80,
    parent_span_id: "s1",
    depth: 1,
  },
  {
    span_id: "s3",
    service: "db",
    operation: "SELECT users",
    status: "error" as const,
    duration_ms: 45,
    parent_span_id: "s2",
    depth: 2,
  },
];

describe("CorrelationTrackerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <CorrelationTrackerCard traceId="abc123" spans={spans} appName="My App" />,
    );
    expect(container.textContent).toContain("Trace");
    expect(container.textContent).toContain("My App");
  });

  it("shows trace id", () => {
    const { container } = render(
      <CorrelationTrackerCard traceId="abc123def" spans={spans} appName="App" />,
    );
    expect(container.textContent).toContain("abc123def");
  });

  it("shows error count", () => {
    const { container } = render(
      <CorrelationTrackerCard traceId="t1" spans={spans} appName="App" />,
    );
    expect(container.textContent).toContain("1 errors");
  });

  it("renders service and operation", () => {
    const { container } = render(
      <CorrelationTrackerCard traceId="t1" spans={spans} appName="App" />,
    );
    expect(container.textContent).toContain("api-gw");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("user-svc");
  });

  it("shows duration", () => {
    const { container } = render(
      <CorrelationTrackerCard traceId="t1" spans={spans} appName="App" />,
    );
    expect(container.textContent).toContain("150.0ms");
  });

  it("shows span count and total", () => {
    const { container } = render(
      <CorrelationTrackerCard traceId="t1" spans={spans} appName="App" />,
    );
    expect(container.textContent).toContain("3 spans");
    expect(container.textContent).toContain("150ms total");
  });

  it("shows empty state", () => {
    const { container } = render(<CorrelationTrackerCard traceId="t1" spans={[]} appName="App" />);
    expect(container.textContent).toContain("No spans");
  });
});
