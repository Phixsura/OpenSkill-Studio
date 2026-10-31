import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogEntryCard } from "@/components/changelog-entry-card";

describe("ChangelogEntryCard", () => {
  const categories = [
    { type: "feature", items: ["Dark mode", "Export CSV"] },
    { type: "fix", items: ["Login crash"] },
  ];
  it("renders", () => {
    const { container } = render(
      <ChangelogEntryCard version="2.1.0" date="2026-10-23" categories={categories}
        totalChanges={3} hasBreaking={false} />
    );
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("2026-10-23");
    expect(container.textContent).toContain("3 changes");
    expect(container.textContent).toContain("✨");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("🐛");
    expect(container.textContent).toContain("Login crash");
  });
  it("breaking badge", () => {
    const { container } = render(
      <ChangelogEntryCard version="3.0" date="2026-10-23" categories={[]}
        totalChanges={1} hasBreaking={true} />
    );
    expect(container.textContent).toContain("Breaking");
  });
});
