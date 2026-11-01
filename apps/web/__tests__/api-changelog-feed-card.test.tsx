import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogFeedCard from "../src/components/api-changelog-feed-card";

const entries = [
  {
    entry_id: "e1",
    version: "v2.0",
    title: "New Release",
    summary: "Major update with breaking changes",
  },
  { entry_id: "e2", version: "v1.5", title: "Bug Fixes", summary: "Minor patches" },
];

describe("APIChangelogFeedCard", () => {
  it("renders header with pagination", () => {
    const { container } = render(
      <APIChangelogFeedCard
        entries={entries}
        totalCount={15}
        currentPage={1}
        totalPages={2}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Changelog Feed");
    expect(container.textContent).toContain("15 entries");
    expect(container.textContent).toContain("page 1/2");
  });

  it("shows titles and versions", () => {
    const { container } = render(
      <APIChangelogFeedCard
        entries={entries}
        totalCount={2}
        currentPage={1}
        totalPages={1}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("New Release");
    expect(container.textContent).toContain("v2.0");
  });

  it("shows summaries", () => {
    const { container } = render(
      <APIChangelogFeedCard
        entries={entries}
        totalCount={2}
        currentPage={1}
        totalPages={1}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Major update");
  });

  it("shows empty state", () => {
    const { container } = render(
      <APIChangelogFeedCard
        entries={[]}
        totalCount={0}
        currentPage={1}
        totalPages={1}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("No changelog entries");
  });
});
