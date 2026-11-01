import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-changelog-feed-card";

describe("ChangelogFeedCard", () => {
  it("shows feed", () => {
    const items = [{ entry_id: "e1", version: "v2.0", title: "New auth flow", change_type: "feature", relevant: true, read: false }];
    const { container } = render(<Card items={items} unreadCount={1} appName="App" />);
    expect(container.textContent).toContain("Changelog Feed");
    expect(container.textContent).toContain("1 new");
    expect(container.textContent).toContain("New auth flow");
    expect(container.textContent).toContain("v2.0");
  });
  it("shows empty", () => {
    const { container } = render(<Card items={[]} unreadCount={0} appName="App" />);
    expect(container.textContent).toContain("No changelog entries");
  });
});
