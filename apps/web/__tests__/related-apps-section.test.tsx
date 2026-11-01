import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RelatedAppsSection } from "@/components/related-apps-section";

describe("RelatedAppsSection", () => {
  it("renders sections", () => {
    const sections = [
      { key: "category", title: "Similar Apps", apps: [{ id: "a1", name: "App A" }], count: 1 },
      { key: "tags", title: "By Tags", apps: [], count: 0 },
    ];
    const { container } = render(<RelatedAppsSection sections={sections} />);
    expect(container.textContent).toContain("Similar Apps");
    expect(container.textContent).toContain("App A");
    expect(container.textContent).not.toContain("By Tags"); // hidden when empty
  });
  it("hidden when all empty", () => {
    const sections = [{ key: "a", title: "A", apps: [], count: 0 }];
    const { container } = render(<RelatedAppsSection sections={sections} />);
    expect(container.innerHTML).toBe("");
  });
});
