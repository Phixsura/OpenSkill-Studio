import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-invite-code-card";

describe("ConsumerInviteCodeCard", () => {
  it("shows invites", () => {
    const invites = [{ code: "ABC123DEF456", usedCount: 3, maxUses: 10, disabled: false, expiresAt: "2026-07-01", planId: "pro" }];
    const { container } = render(<Card invites={invites} appName="App" />);
    expect(container.textContent).toContain("Invite Codes");
    expect(container.textContent).toContain("ABC123DEF456");
    expect(container.textContent).toContain("3/10 used");
    expect(container.textContent).toContain("pro");
  });
  it("shows empty", () => {
    const { container } = render(<Card invites={[]} appName="App" />);
    expect(container.textContent).toContain("No invite codes");
  });
});
