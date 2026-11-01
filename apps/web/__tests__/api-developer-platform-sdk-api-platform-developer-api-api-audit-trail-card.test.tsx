import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-audit-trail-card";

describe("AuditTrailCard", () => {
  it("shows events", () => {
    const events = [{ event_id: "e1", actor_id: "admin-1", actor_type: "admin", action: "key.create", resource_type: "api_key" }];
    const { container } = render(<Card events={events} totalCount={500} securityEventCount={10} appName="App" />);
    expect(container.textContent).toContain("Audit Trail");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("10 security");
    expect(container.textContent).toContain("admin-1");
    expect(container.textContent).toContain("key.create");
  });
  it("shows empty", () => {
    const { container } = render(<Card events={[]} totalCount={0} securityEventCount={0} appName="App" />);
    expect(container.textContent).toContain("No audit events");
  });
});
