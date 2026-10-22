import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RequestInspectorPanel } from "@/components/request-inspector-panel";

describe("RequestInspectorPanel", () => {
  it("renders requests", () => {
    const requests = [
      { method: "GET", path: "/api/v1/apps", status_code: 200, duration_ms: 45, captured_at: "" },
      { method: "POST", path: "/api/v1/install", status_code: 500, duration_ms: 200, captured_at: "" },
    ];
    const { container } = render(<RequestInspectorPanel requests={requests} />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/v1/apps");
    expect(container.textContent).toContain("500");
  });
  it("empty state", () => {
    const { container } = render(<RequestInspectorPanel requests={[]} />);
    expect(container.textContent).toContain("No requests");
  });
});
