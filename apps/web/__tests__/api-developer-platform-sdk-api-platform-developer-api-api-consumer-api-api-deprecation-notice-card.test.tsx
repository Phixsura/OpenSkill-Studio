import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-deprecation-notice-card";

describe("DeprecationNoticeCard", () => {
  it("shows notices", () => {
    const notices = [{ notice_id: "n1", endpoint: "/v1/users", method: "GET", urgency: "warning", message: "Use /v2/users", sunset_date: "2025-06-01", acknowledged_count: 3 }];
    const { container } = render(<Card notices={notices} urgentCount={0} appName="App" />);
    expect(container.textContent).toContain("Deprecation Notices");
    expect(container.textContent).toContain("/v1/users");
    expect(container.textContent).toContain("2025-06-01");
    expect(container.textContent).toContain("Use /v2/users");
  });
  it("shows urgent count", () => {
    const { container } = render(<Card notices={[]} urgentCount={2} appName="App" />);
    expect(container.textContent).toContain("2 urgent");
  });
});
