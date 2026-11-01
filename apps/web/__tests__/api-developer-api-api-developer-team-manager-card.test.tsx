import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperTeamManagerCard from "../src/components/api-developer-api-api-developer-team-manager-card";

const teams = [{
  team_id: "t1", name: "API Team", member_count: 3,
  members: [{ developer_id: "alice", role: "owner" }, { developer_id: "bob", role: "developer" }],
}];

describe("APIDeveloperAPIApiDeveloperTeamManagerCard", () => {
  it("shows teams", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperTeamManagerCard teams={teams} appName="App" />);
    expect(container.textContent).toContain("Developer Teams");
    expect(container.textContent).toContain("API Team");
    expect(container.textContent).toContain("3 members");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("bob");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperTeamManagerCard teams={[]} appName="App" />);
    expect(container.textContent).toContain("No teams");
  });
});
