import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReleaseNotesView } from "@/components/release-notes-view";

describe("ReleaseNotesView", () => {
  const categories = {
    feature: [{ title: "Dark mode", description: "New theme", icon: "✨", pr: 42, author: "Alice" }],
    fix: [{ title: "Login crash", description: "", icon: "🐛", pr: null, author: "Bob" }],
  };
  it("renders release notes", () => {
    const { container } = render(
      <ReleaseNotesView version="2.0.0" date="2026-03-01" categories={categories} hasBreaking={true} hasSecurity={false} />
    );
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("Dark mode");
    expect(container.textContent).toContain("#42");
    expect(container.textContent).toContain("by Alice");
    expect(container.textContent).toContain("Login crash");
  });
});
