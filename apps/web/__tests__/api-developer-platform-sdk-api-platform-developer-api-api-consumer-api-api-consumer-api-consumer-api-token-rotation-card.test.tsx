import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-token-rotation-card";

describe("ConsumerApiTokenRotationCard", () => {
  it("shows tokens", () => {
    const tokens = [
      { id: "tok_abc123", createdAt: "2026-06-01", expiresAt: "2026-09-01", revoked: false, hasPredecessor: false },
      { id: "tok_def456", createdAt: "2026-05-01", expiresAt: "2026-08-01", revoked: true, hasPredecessor: true },
    ];
    const { container } = render(<Card tokens={tokens} consumerId="c1" gracePeriodHours={24} appName="App" />);
    expect(container.textContent).toContain("Token Rotation");
    expect(container.textContent).toContain("tok_abc123");
    expect(container.textContent).toContain("revoked");
    expect(container.textContent).toContain("1 active / 2 total");
    expect(container.textContent).toContain("Grace: 24h");
  });
  it("shows empty", () => {
    const { container } = render(<Card tokens={[]} consumerId="c1" gracePeriodHours={24} appName="App" />);
    expect(container.textContent).toContain("No tokens");
  });
});
