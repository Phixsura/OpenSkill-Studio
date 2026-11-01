import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-changelog-card";

describe("ConsumerApiChangelogCard", () => {
  it("shows entries and unread", () => {
    const entries = [{ id: "e1", version: "2.0", title: "OAuth2 Support", type: "feature", publishedAt: "2026-06-01" }];
    const { container } = render(<Card entries={entries} unreadCount={3} appName="App" />);
    expect(container.textContent).toContain("API Changelog");
    expect(container.textContent).toContain("OAuth2 Support");
    expect(container.textContent).toContain("feature");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("3 new");
  });
  it("shows empty", () => {
    const { container } = render(<Card entries={[]} unreadCount={0} appName="App" />);
    expect(container.textContent).toContain("No changelog entries");
  });
});
