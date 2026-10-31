import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIChangelogReleaseTrackerCard from "../src/components/api-developer-api-changelog-release-tracker-card";

const releases = [{ version: "v3.0", release_date: "2024-01-15", entry_count: 10, breaking_count: 2 }];

describe("APIDeveloperAPIChangelogReleaseTrackerCard", () => {
  it("shows releases", () => {
    const { container } = render(<APIDeveloperAPIChangelogReleaseTrackerCard releases={releases} totalReleases={5} totalEntries={30} appName="App" />);
    expect(container.textContent).toContain("Release Tracker");
    expect(container.textContent).toContain("5 releases");
    expect(container.textContent).toContain("v3.0");
    expect(container.textContent).toContain("2 breaking");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIChangelogReleaseTrackerCard releases={[]} totalReleases={0} totalEntries={0} appName="App" />);
    expect(container.textContent).toContain("No releases tracked");
  });
});
