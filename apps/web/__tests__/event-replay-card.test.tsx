import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EventReplayCard from "../src/components/event-replay-card";

const events = [
  { event_id: "e1", event_type: "webhook.sent", source: "api", replayed: true },
  { event_id: "e2", event_type: "user.created", source: "auth", replayed: false },
];

const eventTypes = ["user.created", "webhook.sent"];

describe("EventReplayCard", () => {
  it("renders header and counts", () => {
    const { container } = render(
      <EventReplayCard events={events} eventTypes={eventTypes} totalCount={50} appName="App" />,
    );
    expect(container.textContent).toContain("Event Replay");
    expect(container.textContent).toContain("50 events");
    expect(container.textContent).toContain("2 types");
  });

  it("shows event type chips", () => {
    const { container } = render(
      <EventReplayCard events={events} eventTypes={eventTypes} totalCount={2} appName="App" />,
    );
    expect(container.textContent).toContain("webhook.sent");
    expect(container.textContent).toContain("user.created");
  });

  it("shows events with source", () => {
    const { container } = render(
      <EventReplayCard events={events} eventTypes={eventTypes} totalCount={2} appName="App" />,
    );
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("auth");
  });

  it("shows replayed indicator", () => {
    const { container } = render(
      <EventReplayCard events={events} eventTypes={eventTypes} totalCount={2} appName="App" />,
    );
    expect(container.textContent).toContain("replayed");
  });

  it("shows empty state", () => {
    const { container } = render(
      <EventReplayCard events={[]} eventTypes={[]} totalCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("No events stored");
  });
});
