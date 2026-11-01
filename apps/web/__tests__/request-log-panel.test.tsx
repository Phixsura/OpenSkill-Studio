import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RequestLogPanel } from "@/components/request-log-panel";

const mockEntries = [
  { method: "GET", path: "/api/users", statusCode: 200, latencyMs: 45 },
  { method: "POST", path: "/api/data", statusCode: 500, latencyMs: 120 },
];
const mockStats = { total: 100, avgLatency: 55, errorCount: 5 };

describe("RequestLogPanel", () => {
  it("renders entries and stats", () => {
    const { container } = render(<RequestLogPanel entries={mockEntries} stats={mockStats} />);
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("100 reqs");
    expect(container.textContent).toContain("5 errors");
  });
});
