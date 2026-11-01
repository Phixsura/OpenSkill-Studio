import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIActivityTimelineCard from "../src/components/api-developer-api-activity-timeline-card";

const events = [
  { event_id: "e1", actor: "alice", action: "created", resource: "API Key k1" },
  { event_id: "e2", actor: "bob", action: "deleted", resource: "Webhook wh1" },
];

describe("APIDeveloperAPIActivityTimelineCard", () => {
  it("shows timeline", () => {
    const { container } = render(<APIDeveloperAPIActivityTimelineCard events={events} totalCount={100} appName="App" />);
    expect(container.textContent).toContain("Activity Timeline");
    expect(container.textContent).toContain("100 events");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("created");
    expect(container.textContent).toContain("API Key k1");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIActivityTimelineCard events={[]} totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No activity");
  });
});
