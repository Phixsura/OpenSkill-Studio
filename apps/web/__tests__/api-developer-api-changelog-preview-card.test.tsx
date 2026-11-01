import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIChangelogPreviewCard from "../src/components/api-developer-api-changelog-preview-card";

const previews = [
  { preview_id: "p1", version: "v3.0", title: "Major Release", entry_count: 5, published: true, reviewer: "alice" },
  { preview_id: "p2", version: "v3.1", title: "Patch", entry_count: 2, published: false, reviewer: "" },
];

describe("APIDeveloperAPIChangelogPreviewCard", () => {
  it("shows previews", () => {
    const { container } = render(<APIDeveloperAPIChangelogPreviewCard previews={previews} appName="App" />);
    expect(container.textContent).toContain("Changelog Previews");
    expect(container.textContent).toContain("1 drafts / 2 total");
    expect(container.textContent).toContain("Major Release");
    expect(container.textContent).toContain("v3.0");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIChangelogPreviewCard previews={[]} appName="App" />);
    expect(container.textContent).toContain("No previews");
  });
});
