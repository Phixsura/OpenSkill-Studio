import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogTimelineCard from "../src/components/changelog-timeline-card";

const events = [
  {
    event_id: "e1",
    event_type: "release" as const,
    title: "v2.0 Released",
    timestamp: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    event_id: "e2",
    event_type: "incident" as const,
    title: "API Outage",
    timestamp: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    event_id: "e3",
    event_type: "deployment" as const,
    title: "Deployed to prod",
    timestamp: new Date(Date.now() - 86400000).toISOString(),
  },
];

describe("ChangelogTimelineCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ChangelogTimelineCard events={events} appName="My App" />);
    expect(container.textContent).toContain("Timeline");
    expect(container.textContent).toContain("My App");
  });

  it("shows event count", () => {
    const { container } = render(<ChangelogTimelineCard events={events} appName="App" />);
    expect(container.textContent).toContain("3 events");
  });

  it("renders event titles", () => {
    const { container } = render(<ChangelogTimelineCard events={events} appName="App" />);
    expect(container.textContent).toContain("v2.0 Released");
    expect(container.textContent).toContain("API Outage");
    expect(container.textContent).toContain("Deployed to prod");
  });

  it("shows type icons", () => {
    const { container } = render(<ChangelogTimelineCard events={events} appName="App" />);
    expect(container.textContent).toContain("🚀");
    expect(container.textContent).toContain("🔥");
    expect(container.textContent).toContain("📦");
  });

  it("shows empty state", () => {
    const { container } = render(<ChangelogTimelineCard events={[]} appName="App" />);
    expect(container.textContent).toContain("No events");
  });
});
