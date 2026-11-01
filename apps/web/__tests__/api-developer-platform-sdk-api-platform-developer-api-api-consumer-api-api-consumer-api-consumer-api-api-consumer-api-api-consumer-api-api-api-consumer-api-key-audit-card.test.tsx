import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-key-audit-card";

describe("ConsumerApiKeyAuditCard", () => {
  it("shows events", () => {
    const events = [{ id: "e1", keyId: "k1", action: "created", actorId: "admin", timestamp: "12:00" }];
    const counts = { created: 5, revoked: 1 };
    const { container } = render(<Card events={events} counts={counts} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Key Audit Trail");
    expect(container.textContent).toContain("created");
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("created: 5");
  });
  it("shows empty", () => {
    const { container } = render(<Card events={[]} counts={{}} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No key events");
  });
});
