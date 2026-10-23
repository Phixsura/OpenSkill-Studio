import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RequestLogTable } from "@/components/request-log-table";

describe("RequestLogTable", () => {
  const logs = [
    { method: "GET", path: "/api/apps", statusCode: 200, durationMs: 45, success: true, timestamp: "2026-01-01" },
    { method: "POST", path: "/api/apps", statusCode: 500, durationMs: 200, success: false, timestamp: "2026-01-01" },
  ];
  it("renders log table", () => {
    const { container } = render(<RequestLogTable logs={logs} avgDurationMs={122} errorRate={50} />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/apps");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("122ms");
  });
});
