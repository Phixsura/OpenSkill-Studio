import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DeveloperApiReferencePage from "@/app/(dashboard)/dashboard/developer/api-reference/page";

describe("DeveloperApiReferencePage", () => {
  it("renders without crashing", () => {
    const { container } = render(<DeveloperApiReferencePage />);
    expect(container).toBeTruthy();
  });

  it("shows section headings", () => {
    const { container } = render(<DeveloperApiReferencePage />);
    expect(container.textContent).toContain("Developer Accounts");
  });

  it("has interactive elements", () => {
    const { container } = render(<DeveloperApiReferencePage />);
    const interactive = container.querySelectorAll("button, details, [role='button']");
    expect(interactive.length).toBeGreaterThan(0);
  });
});
