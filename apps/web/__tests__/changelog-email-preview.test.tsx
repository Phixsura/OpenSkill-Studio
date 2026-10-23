import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogEmailPreview } from "@/components/changelog-email-preview";

describe("ChangelogEmailPreview", () => {
  it("renders email", () => {
    const { container } = render(
      <ChangelogEmailPreview subject="v3.5 Released!" greeting="Hi Alice," version="3.5.0"
        totalChanges={3} sections={[
          { type: "added", emoji: "✨", items: ["SSO", "Dark mode"], count: 2 },
          { type: "fixed", emoji: "🐛", items: ["Login bug"], count: 1 },
        ]} />
    );
    expect(container.textContent).toContain("v3.5 Released!");
    expect(container.textContent).toContain("Hi Alice,");
    expect(container.textContent).toContain("SSO");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("Login bug");
    expect(container.textContent).toContain("3 total changes");
  });
});
