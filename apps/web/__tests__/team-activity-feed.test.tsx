import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TeamActivityFeed } from "@/components/team-activity-feed";

describe("TeamActivityFeed", () => {
  it("renders feed", () => {
    const { container } = render(
      <TeamActivityFeed total={3} topContributor="alice" items={[
        { user: "alice", type: "deploy", message: "Deploy v3.1", timestamp: "2026-10-24T12:00:00Z", icon: "🚀" },
        { user: "bob", type: "review", message: "LGTM", timestamp: "2026-10-24T11:00:00Z", icon: "👀" },
      ]} />
    );
    expect(container.textContent).toContain("Team Activity");
    expect(container.textContent).toContain("3 events");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("Deploy v3.1");
    expect(container.textContent).toContain("Top contributor");
  });
});
