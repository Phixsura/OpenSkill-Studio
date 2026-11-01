import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogSubscriberCard from "../src/components/changelog-subscriber-card";

const subscribers = [
  {
    subscriber_id: "s1",
    email: "alice@example.com",
    name: "Alice",
    active: true,
    delivery_count: 12,
  },
  { subscriber_id: "s2", email: "bob@example.com", name: "", active: false, delivery_count: 5 },
];

describe("ChangelogSubscriberCard", () => {
  it("renders header and active count", () => {
    const { container } = render(
      <ChangelogSubscriberCard subscribers={subscribers} activeCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("Changelog Subscribers");
    expect(container.textContent).toContain("1 active");
  });

  it("shows names and emails", () => {
    const { container } = render(
      <ChangelogSubscriberCard subscribers={subscribers} activeCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("bob@example.com");
  });

  it("shows delivery counts", () => {
    const { container } = render(
      <ChangelogSubscriberCard subscribers={subscribers} activeCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("12 sent");
  });

  it("shows empty state", () => {
    const { container } = render(
      <ChangelogSubscriberCard subscribers={[]} activeCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("No subscribers");
  });
});
