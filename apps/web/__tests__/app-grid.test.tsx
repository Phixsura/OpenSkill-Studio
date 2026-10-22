import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppGrid } from "@/components/app-grid";

const APPS = [
  { id: "1", name: "App One", slug: "one", category: "connector", description: "First app", installCount: 100 },
  { id: "2", name: "App Two", slug: "two", category: "automation", description: null, installCount: 50 },
];

describe("AppGrid", () => {
  it("shows apps", () => {
    const { container } = render(<AppGrid apps={APPS} />);
    expect(container.textContent).toContain("App One");
    expect(container.textContent).toContain("App Two");
  });
  it("shows empty state", () => {
    const { container } = render(<AppGrid apps={[]} />);
    expect(container.textContent).toContain("No apps");
  });
  it("has links", () => {
    const { container } = render(<AppGrid apps={APPS} />);
    expect(container.querySelectorAll("a").length).toBe(2);
  });
});
