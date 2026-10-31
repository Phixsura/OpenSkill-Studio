import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIEventBusCard from "../src/components/api-event-bus-card";

const topics = [
  { topic_id: "t1", name: "User Events", subscriber_count: 3, publish_count: 150 },
  { topic_id: "t2", name: "System Events", subscriber_count: 1, publish_count: 50 },
];

describe("APIEventBusCard", () => {
  it("renders header and totals", () => {
    const { container } = render(<APIEventBusCard topics={topics} appName="App" />);
    expect(container.textContent).toContain("Event Bus");
    expect(container.textContent).toContain("2 topics");
    expect(container.textContent).toContain("200 published");
  });

  it("shows topic details", () => {
    const { container } = render(<APIEventBusCard topics={topics} appName="App" />);
    expect(container.textContent).toContain("User Events");
    expect(container.textContent).toContain("3 subs");
    expect(container.textContent).toContain("150 pubs");
  });

  it("shows empty state", () => {
    const { container } = render(<APIEventBusCard topics={[]} appName="App" />);
    expect(container.textContent).toContain("No event topics");
  });
});
