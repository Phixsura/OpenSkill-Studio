import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-invitation-card";

describe("ConsumerInvitationCard", () => {
  it("shows invites", () => {
    const invites = [{ invite_id: "i1", email: "dev@example.com", role: "consumer", status: "pending", hours_remaining: 48 }];
    const { container } = render(<Card invites={invites} pendingCount={1} appName="App" />);
    expect(container.textContent).toContain("Invitations");
    expect(container.textContent).toContain("dev@example.com");
    expect(container.textContent).toContain("1 pending");
  });
  it("shows empty", () => {
    const { container } = render(<Card invites={[]} pendingCount={0} appName="App" />);
    expect(container.textContent).toContain("No invitations");
  });
});
