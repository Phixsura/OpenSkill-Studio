import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionEventTimeline } from "@/components/extension-event-timeline";

const mockEvents = [
  { id: "1", type: "publish" as const, title: "v2.0.0 Published", description: "Major release with new features", timestamp: "1h ago", actor: "alice", metadata: { version: "2.0.0" } },
  { id: "2", type: "install" as const, title: "Installed by Acme Corp", description: "First enterprise install", timestamp: "3h ago", actor: "bob" },
  { id: "3", type: "review" as const, title: "New 5-star review", description: "Great extension!", timestamp: "1d ago", actor: "carol" },
  { id: "4", type: "incident" as const, title: "High error rate detected", description: "Error rate exceeded 5% threshold", timestamp: "2d ago", actor: "system" },
];

describe("ExtensionEventTimeline", () => {
  it("renders extension name and events", () => {
    const { container } = render(
      <ExtensionEventTimeline events={mockEvents} extensionName="Slack Bot" />
    );
    expect(container.textContent).toContain("Slack Bot Timeline");
    expect(container.textContent).toContain("v2.0.0 Published");
    expect(container.textContent).toContain("Installed by Acme Corp");
  });

  it("shows event types and actors", () => {
    const { container } = render(
      <ExtensionEventTimeline events={mockEvents} extensionName="Test" />
    );
    expect(container.textContent).toContain("publish");
    expect(container.textContent).toContain("install");
    expect(container.textContent).toContain("by alice");
    expect(container.textContent).toContain("by system");
  });

  it("renders metadata", () => {
    const { container } = render(
      <ExtensionEventTimeline events={mockEvents} extensionName="Test" />
    );
    expect(container.textContent).toContain("version: 2.0.0");
  });

  it("shows incident events", () => {
    const { container } = render(
      <ExtensionEventTimeline events={mockEvents} extensionName="Test" />
    );
    expect(container.textContent).toContain("High error rate");
    expect(container.textContent).toContain("incident");
  });
});
