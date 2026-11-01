import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DeveloperTutorialPage from "@/app/(dashboard)/dashboard/developer/tutorial/page";
import DeveloperDocsPage from "@/app/(dashboard)/dashboard/developer/docs/page";

describe("DeveloperTutorialPage", () => {
  it("renders", () => {
    const { container } = render(<DeveloperTutorialPage />);
    expect(container.textContent).toContain("Build Your First App");
  });

  it("has step sections", () => {
    const { container } = render(<DeveloperTutorialPage />);
    const headings = container.querySelectorAll("h2");
    expect(headings.length).toBeGreaterThanOrEqual(3);
  });
});

describe("DeveloperDocsPage", () => {
  it("renders", () => {
    const { container } = render(<DeveloperDocsPage />);
    expect(container.textContent).toContain("Developer Documentation");
  });

  it("has Quick Start section", () => {
    const { container } = render(<DeveloperDocsPage />);
    expect(container.textContent).toContain("Quick Start");
  });

  it("has documentation links", () => {
    const { container } = render(<DeveloperDocsPage />);
    const links = container.querySelectorAll("a");
    expect(links.length).toBeGreaterThan(0);
  });
});
