import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangeTrackerTimeline } from "@/components/change-tracker-timeline";

describe("ChangeTrackerTimeline", () => {
  it("renders changes", () => {
    const { container } = render(
      <ChangeTrackerTimeline total={10} byAction={{ deployed: 5, updated: 3 }}
        changes={[
          { id: 3, entity: "api-service", action: "deployed", user: "alice", details: "v2.0" },
          { id: 2, entity: "config", action: "updated", user: "bob", details: "Changed timeout" },
        ]} />
    );
    expect(container.textContent).toContain("Change Tracker");
    expect(container.textContent).toContain("10 changes");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("deployed");
    expect(container.textContent).toContain("api-service");
    expect(container.textContent).toContain("Changed timeout");
  });
});
