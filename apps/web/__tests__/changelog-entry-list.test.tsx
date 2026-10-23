import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogEntryList } from "@/components/changelog-entry-list";

describe("ChangelogEntryList", () => {
  it("renders changelog", () => {
    const { container } = render(
      <ChangelogEntryList version="3.5.0" total={3} hasBreaking={true}
        sections={[
          { type: "added", emoji: "✨", label: "Added", count: 2, entries: [
            { title: "SSO", description: "SAML support", breaking: false },
            { title: "Dark mode", description: "", breaking: false },
          ]},
          { type: "removed", emoji: "🗑️", label: "Removed", count: 1, entries: [
            { title: "Legacy API", description: "", breaking: true },
          ]},
        ]} />
    );
    expect(container.textContent).toContain("v3.5.0");
    expect(container.textContent).toContain("3 changes");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("SSO");
    expect(container.textContent).toContain("Added (2)");
    expect(container.textContent).toContain("[BREAKING]");
  });
});
