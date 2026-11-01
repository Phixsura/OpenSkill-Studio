import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-team-member-card";

describe("ConsumerTeamMemberCard", () => {
  it("shows members", () => {
    const members = [{ id: "m1", email: "admin@co.com", role: "owner", joinedAt: "2026-01-01" }, { id: "m2", email: "dev@co.com", role: "member", joinedAt: "2026-03-01" }];
    const { container } = render(<Card members={members} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Team Members");
    expect(container.textContent).toContain("admin@co.com");
    expect(container.textContent).toContain("owner");
    expect(container.textContent).toContain("2 members");
  });
  it("shows empty", () => {
    const { container } = render(<Card members={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No team members");
  });
});
