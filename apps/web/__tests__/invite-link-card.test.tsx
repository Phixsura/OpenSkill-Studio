import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import InviteLinkCard from "../src/components/invite-link-card";

const links = [
  {
    invite_id: "inv-1",
    code: "abc123defghijklmnop",
    role: "admin",
    max_uses: 5,
    uses: 2,
    is_valid: true,
    created_by: "alice",
  },
  {
    invite_id: "inv-2",
    code: "xyz789uvwqrstabcdef",
    role: "member",
    max_uses: 0,
    uses: 10,
    is_valid: false,
    created_by: "bob",
  },
];

describe("InviteLinkCard", () => {
  it("renders header and valid count", () => {
    const { container } = render(<InviteLinkCard links={links} appName="App" />);
    expect(container.textContent).toContain("Invite Links");
    expect(container.textContent).toContain("1/2 valid");
  });

  it("shows truncated codes and roles", () => {
    const { container } = render(<InviteLinkCard links={links} appName="App" />);
    expect(container.textContent).toContain("abc123de...");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("member");
  });

  it("shows usage counts", () => {
    const { container } = render(<InviteLinkCard links={links} appName="App" />);
    expect(container.textContent).toContain("2/5 used");
    expect(container.textContent).toContain("10 used");
  });

  it("shows empty state", () => {
    const { container } = render(<InviteLinkCard links={[]} appName="App" />);
    expect(container.textContent).toContain("No invite links");
  });
});
