import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TeamMemberCard from "../src/components/team-member-card";

const members = [
  { user_id: "u1", email: "alice@x.com", display_name: "Alice", role: "owner" as const },
  { user_id: "u2", email: "bob@x.com", display_name: "Bob", role: "admin" as const },
  { user_id: "u3", email: "carol@x.com", display_name: "Carol", role: "viewer" as const },
];

describe("TeamMemberCard", () => {
  it("renders header", () => {
    const { container } = render(<TeamMemberCard members={members} appName="My App" />);
    expect(container.textContent).toContain("Team Members");
  });

  it("shows member count", () => {
    const { container } = render(<TeamMemberCard members={members} appName="App" />);
    expect(container.textContent).toContain("3 members");
  });

  it("renders names and emails", () => {
    const { container } = render(<TeamMemberCard members={members} appName="App" />);
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("alice@x.com");
  });

  it("shows role badges", () => {
    const { container } = render(<TeamMemberCard members={members} appName="App" />);
    expect(container.textContent).toContain("owner");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("viewer");
  });

  it("shows empty state", () => {
    const { container } = render(<TeamMemberCard members={[]} appName="App" />);
    expect(container.textContent).toContain("No team members");
  });
});
