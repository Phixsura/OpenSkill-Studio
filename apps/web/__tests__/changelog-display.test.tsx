import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogDisplay } from "@/components/changelog-display";

describe("ChangelogDisplay", () => {
  const sections = [
    { title: "Features", items: ["Login page", "Dark mode"] },
    { title: "Bug Fixes", items: ["Typo fix"] },
  ];
  it("renders", () => {
    const { container } = render(
      <ChangelogDisplay version="1.2.0" date="2026-10-23" sections={sections}
        breakingChanges={["New API surface"]} />
    );
    expect(container.textContent).toContain("v1.2.0");
    expect(container.textContent).toContain("2026-10-23");
    expect(container.textContent).toContain("Breaking Changes");
    expect(container.textContent).toContain("Login page");
    expect(container.textContent).toContain("Typo fix");
  });
  it("no breaking", () => {
    const { container } = render(
      <ChangelogDisplay version="1.0.1" date="2026-01-01" sections={sections} />
    );
    expect(container.textContent).not.toContain("Breaking");
  });
});
