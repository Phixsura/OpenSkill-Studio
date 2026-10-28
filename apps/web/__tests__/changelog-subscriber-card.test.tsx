import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogSubscriberCard from "../src/components/changelog-subscriber-card";

const subs = [
  {
    subscriber_id: "s1",
    channel: "email",
    target: "dev@example.com",
    release_types: ["major", "security"],
    active: true,
    notification_count: 5,
  },
  {
    subscriber_id: "s2",
    channel: "webhook",
    target: "https://hooks.example.com",
    release_types: null,
    active: true,
    notification_count: 12,
  },
  {
    subscriber_id: "s3",
    channel: "in_app",
    target: "user-42",
    release_types: null,
    active: false,
    notification_count: 3,
  },
];

describe("ChangelogSubscriberCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<ChangelogSubscriberCard subscribers={subs} appName="My App" />);
    expect(container.textContent).toContain("Changelog Subscribers");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(<ChangelogSubscriberCard subscribers={subs} appName="App" />);
    expect(container.textContent).toContain("2 active");
  });

  it("renders targets and channel icons", () => {
    const { container } = render(<ChangelogSubscriberCard subscribers={subs} appName="App" />);
    expect(container.textContent).toContain("dev@example.com");
    expect(container.textContent).toContain("✉️");
    expect(container.textContent).toContain("🔗");
  });

  it("shows release type filters", () => {
    const { container } = render(<ChangelogSubscriberCard subscribers={subs} appName="App" />);
    expect(container.textContent).toContain("major, security");
  });

  it("shows all-releases for unfiltered", () => {
    const { container } = render(<ChangelogSubscriberCard subscribers={subs} appName="App" />);
    expect(container.textContent).toContain("all releases");
  });

  it("shows notification count", () => {
    const { container } = render(<ChangelogSubscriberCard subscribers={subs} appName="App" />);
    expect(container.textContent).toContain("12 sent");
  });

  it("shows unsubscribed label", () => {
    const { container } = render(<ChangelogSubscriberCard subscribers={subs} appName="App" />);
    expect(container.textContent).toContain("unsubscribed");
  });

  it("shows empty state", () => {
    const { container } = render(<ChangelogSubscriberCard subscribers={[]} appName="App" />);
    expect(container.textContent).toContain("No subscribers");
  });
});
