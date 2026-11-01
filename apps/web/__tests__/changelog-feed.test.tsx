import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogFeed } from "@/components/changelog-feed";

describe("ChangelogFeed", () => {
  it("shows empty state", () => {
    const { container } = render(<ChangelogFeed entries={[]} />);
    expect(container.textContent).toContain("No changelog entries");
  });
  it("renders entries", () => {
    const entries = [{ entryId: "cl-1", extensionId: "ext-1", version: "1.0.0", changes: ["Initial release", "Added auth"], changeType: "feature", publishedAt: Date.now() }];
    const { container } = render(<ChangelogFeed entries={entries} />);
    expect(container.textContent).toContain("ext-1");
    expect(container.textContent).toContain("v1.0.0");
    expect(container.textContent).toContain("Initial release");
  });
});
