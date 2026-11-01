import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogRssPreview } from "@/components/changelog-rss-preview";

describe("ChangelogRssPreview", () => {
  it("renders preview", () => {
    const { container } = render(
      <ChangelogRssPreview title="OpenSkill Changelog" lastUpdated="2026-10-24"
        items={[
          { title: "v3.5 Released", version: "3.5.0", date: "2026-10-24", description: "SSO support", changeCount: 15 },
        ]} />
    );
    expect(container.textContent).toContain("OpenSkill Changelog");
    expect(container.textContent).toContain("v3.5 Released");
    expect(container.textContent).toContain("15 changes");
    expect(container.textContent).toContain("SSO support");
  });
});
