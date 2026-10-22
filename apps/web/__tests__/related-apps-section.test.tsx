import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RelatedAppsSection } from "@/components/related-apps-section";

describe("RelatedAppsSection", () => {
  it("shows apps", () => {
    const { container } = render(<RelatedAppsSection apps={[{ name: "Rel App", slug: "rel", category: "connector", installCount: 42 }]} />);
    expect(container.textContent).toContain("Rel App");
    expect(container.textContent).toContain("Related Apps");
  });
  it("null when empty", () => {
    const { container } = render(<RelatedAppsSection apps={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
