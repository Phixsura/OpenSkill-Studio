import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogFeed } from "@/components/changelog-feed";

const MOCK_ENTRIES = [
  {
    version: "2.1.0",
    title: "Dashboard Improvements",
    items: [
      { category: "added" as const, description: "New analytics widget", breaking: false },
      { category: "fixed" as const, description: "OAuth token refresh", breaking: false },
      { category: "changed" as const, description: "API response format", breaking: true },
    ],
    published_at: "2026-10-25T00:00:00Z",
    has_breaking: true,
  },
  {
    version: "2.0.0",
    title: "Major Release",
    items: [
      { category: "added" as const, description: "Webhook support", breaking: false },
      { category: "removed" as const, description: "Legacy v1 endpoints", breaking: true },
      { category: "security" as const, description: "Fixed XSS in embed", breaking: false },
    ],
    published_at: "2026-10-10T00:00:00Z",
    has_breaking: true,
  },
];

describe("ChangelogFeed", () => {
  it("renders heading and app name", () => {
    const { container } = render(<ChangelogFeed appName="My App" entries={MOCK_ENTRIES} />);
    expect(container.textContent).toContain("Changelog");
    expect(container.textContent).toContain("My App");
  });

  it("renders release count", () => {
    const { container } = render(<ChangelogFeed appName="App" entries={MOCK_ENTRIES} />);
    expect(container.textContent).toContain("2 releases");
  });

  it("renders version numbers", () => {
    const { container } = render(<ChangelogFeed appName="App" entries={MOCK_ENTRIES} />);
    expect(container.textContent).toContain("2.1.0");
    expect(container.textContent).toContain("2.0.0");
  });

  it("renders entry titles", () => {
    const { container } = render(<ChangelogFeed appName="App" entries={MOCK_ENTRIES} />);
    expect(container.textContent).toContain("Dashboard Improvements");
    expect(container.textContent).toContain("Major Release");
  });

  it("renders BREAKING badge", () => {
    const { container } = render(<ChangelogFeed appName="App" entries={MOCK_ENTRIES} />);
    expect(container.textContent).toContain("BREAKING");
  });

  it("renders category badges", () => {
    const { container } = render(<ChangelogFeed appName="App" entries={MOCK_ENTRIES} />);
    expect(container.textContent).toContain("Added");
    expect(container.textContent).toContain("Fixed");
    expect(container.textContent).toContain("Changed");
    expect(container.textContent).toContain("Removed");
    expect(container.textContent).toContain("Security");
  });

  it("renders item descriptions", () => {
    const { container } = render(<ChangelogFeed appName="App" entries={MOCK_ENTRIES} />);
    expect(container.textContent).toContain("New analytics widget");
    expect(container.textContent).toContain("OAuth token refresh");
    expect(container.textContent).toContain("Legacy v1 endpoints");
    expect(container.textContent).toContain("Fixed XSS in embed");
  });

  it("renders dates", () => {
    const { container } = render(<ChangelogFeed appName="App" entries={MOCK_ENTRIES} />);
    expect(container.textContent).toContain("2026");
  });

  it("shows empty state", () => {
    const { container } = render(<ChangelogFeed appName="App" entries={[]} />);
    expect(container.textContent).toContain("No changelog entries yet");
  });

  it("marks breaking items with warning", () => {
    const { container } = render(<ChangelogFeed appName="App" entries={MOCK_ENTRIES} />);
    expect(container.textContent).toContain("⚠️");
  });
});
