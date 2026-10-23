import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RequestLogViewer } from "@/components/request-log-viewer";

describe("RequestLogViewer", () => {
  const logs = [
    { request_id: "r1", method: "GET", path: "/api/apps", status_code: 200, latency_ms: 45, level: "info", timestamp: "2026-10-23T12:00:00" },
    { request_id: "r2", method: "POST", path: "/api/x", status_code: 500, latency_ms: 3000, level: "error", timestamp: "2026-10-23T12:01:00" },
  ];
  it("renders", () => {
    const { container } = render(
      <RequestLogViewer logs={logs} totalRequests={2} avgLatencyMs={1522} errorRate={50} />
    );
    expect(container.textContent).toContain("Request Log");
    expect(container.textContent).toContain("2 req");
    expect(container.textContent).toContain("1522ms avg");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
});
