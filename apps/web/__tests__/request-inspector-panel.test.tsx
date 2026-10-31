import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RequestInspectorPanel } from "@/components/request-inspector-panel";

describe("RequestInspectorPanel", () => {
  const request = {
    request_id: "abc123", method: "POST", path: "/api/apps",
    headers: { "Content-Type": "application/json", "Authorization": "***" },
    body_size_bytes: 42, content_type: "application/json",
    has_auth: true, auth_type: "Bearer", timestamp: "2026-10-23T12:00:00",
  };
  it("renders", () => {
    const { container } = render(<RequestInspectorPanel request={request} />);
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("/api/apps");
    expect(container.textContent).toContain("abc123");
    expect(container.textContent).toContain("42 bytes");
    expect(container.textContent).toContain("Bearer ✓");
  });
});
