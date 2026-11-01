import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-token-revocation-log-card";

describe("TokenRevocationLogCard", () => {
  it("shows events", () => {
    const events = [{ id: "e1", tokenId: "t1", reason: "compromise", revokedBy: "admin", timestamp: "12:00" }];
    const { container } = render(<Card events={events} byReason={{ compromise: 1, rotation: 3 }} totalRevocations={4} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Revocation Log");
    expect(container.textContent).toContain("compromise");
    expect(container.textContent).toContain("t1");
    expect(container.textContent).toContain("rotation: 3");
  });
  it("shows empty", () => {
    const { container } = render(<Card events={[]} byReason={{}} totalRevocations={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No revocations");
  });
});
