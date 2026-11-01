import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-audit-trail-card";

describe("ConsumerApiAuditTrailCard", () => {
  it("shows events", () => {
    const events = [{ id: "e1", action: "api_key.created", actorId: "user1", resourceType: "api_key", resourceId: "k1", timestamp: "12:00" }];
    const { container } = render(<Card events={events} consumerId="c1" totalCount={150} appName="App" />);
    expect(container.textContent).toContain("Audit Trail");
    expect(container.textContent).toContain("api_key.created");
    expect(container.textContent).toContain("user1");
    expect(container.textContent).toContain("150 total events");
  });
  it("shows empty", () => {
    const { container } = render(<Card events={[]} consumerId="c1" totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No audit events");
  });
});
