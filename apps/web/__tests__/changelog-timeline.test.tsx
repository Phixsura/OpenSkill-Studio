import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogTimeline } from "@/components/changelog-timeline";

const mockReleases = [
  { version: "2.0.0", date: "2024-06-01", yanked: false, entries: [
    { description: "New plugin system", category: "Added", isBreaking: false },
    { description: "Changed API signature", category: "Changed", isBreaking: true },
  ]},
  { version: "1.0.0", date: "2024-01-01", yanked: false, entries: [
    { description: "Initial release", category: "Added", isBreaking: false },
  ]},
];

describe("ChangelogTimeline", () => {
  it("renders releases with version and date", () => {
    const { container } = render(
      <ChangelogTimeline releases={mockReleases} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("2024-06-01");
    expect(container.textContent).toContain("Breaking");
  });

  it("shows entries for expanded release", () => {
    const { container } = render(
      <ChangelogTimeline releases={mockReleases} extensionName="MyExt" />
    );
    // First release is expanded by default
    expect(container.textContent).toContain("New plugin system");
    expect(container.textContent).toContain("Added");
  });

  it("toggles expand on click", () => {
    const { container, getByText } = render(
      <ChangelogTimeline releases={mockReleases} extensionName="MyExt" />
    );
    // Click first release to collapse
    fireEvent.click(getByText("v2.0.0"));
    expect(container.textContent).not.toContain("New plugin system");
  });

  it("shows yanked badge", () => {
    const yanked = [{ ...mockReleases[0], yanked: true }];
    const { container } = render(
      <ChangelogTimeline releases={yanked} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("YANKED");
  });
});
