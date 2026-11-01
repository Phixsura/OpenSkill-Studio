import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperInviteCard from "../src/components/api-developer-invite-card";

const invites = [
  { invite_id: "i1", email: "alice@dev.com", role: "developer", accepted: false },
  { invite_id: "i2", email: "bob@dev.com", role: "admin", accepted: true },
];

describe("APIDeveloperInviteCard", () => {
  it("renders with pending count", () => {
    const { container } = render(<APIDeveloperInviteCard invites={invites} appName="App" />);
    expect(container.textContent).toContain("1 pending / 2 total");
    expect(container.textContent).toContain("alice@dev.com");
    expect(container.textContent).toContain("admin");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperInviteCard invites={[]} appName="App" />);
    expect(container.textContent).toContain("No invites");
  });
});
