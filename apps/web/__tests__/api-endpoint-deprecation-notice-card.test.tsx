import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIEndpointDeprecationNoticeCard from "../src/components/api-endpoint-deprecation-notice-card";

const notices = [{ notice_id: "n1", method: "GET", path: "/api/v1/users", message: "Use v2", sunset_date: "2025-01-01", replacement: "/api/v2/users", acknowledged_count: 3 }];

describe("APIEndpointDeprecationNoticeCard", () => {
  it("shows notices", () => {
    const { container } = render(<APIEndpointDeprecationNoticeCard notices={notices} appName="App" />);
    expect(container.textContent).toContain("Deprecation Notices");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("sunset 2025-01-01");
    expect(container.textContent).toContain("/api/v2/users");
  });
  it("shows empty", () => {
    const { container } = render(<APIEndpointDeprecationNoticeCard notices={[]} appName="App" />);
    expect(container.textContent).toContain("No deprecation notices");
  });
});
