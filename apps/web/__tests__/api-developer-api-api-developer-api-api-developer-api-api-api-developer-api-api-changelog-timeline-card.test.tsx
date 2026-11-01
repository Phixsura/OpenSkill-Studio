import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiChangelogTimelineCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-developer-api-api-changelog-timeline-card";

const entries = [
  { entry_id: "e1", version: "v2.0", title: "New users endpoint", change_type: "feature" },
  { entry_id: "e2", version: "v2.0", title: "Removed /old", change_type: "breaking" },
];

describe("Card", () => {
  it("shows timeline", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiChangelogTimelineCard entries={entries} typeCounts={{ feature: 1, breaking: 1 }} appName="App" />);
    expect(container.textContent).toContain("Changelog Timeline");
    expect(container.textContent).toContain("New users endpoint");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("Removed /old");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiChangelogTimelineCard entries={[]} typeCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No changes");
  });
});
