import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotesCard from "../src/components/api-developer-api-api-developer-api-api-platform-release-notes-card";

const notes = [{
  version: "v2.0", title: "Major Release", summary: "Big update",
  highlights: ["New API", "Better docs"], breaking_changes: ["Removed /old"],
  published: true,
}];

describe("APIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotesCard", () => {
  it("shows release notes", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotesCard notes={notes} appName="App" />);
    expect(container.textContent).toContain("Release Notes");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("published");
    expect(container.textContent).toContain("New API");
    expect(container.textContent).toContain("1 breaking changes");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiPlatformReleaseNotesCard notes={[]} appName="App" />);
    expect(container.textContent).toContain("No release notes");
  });
});
