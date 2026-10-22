import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GettingStartedGuide } from "@/components/getting-started-guide";

const STEPS = [
  { step: 1, title: "Create Account", description: "Set up profile", docsUrl: "/docs/1" },
  { step: 2, title: "Create App", description: "Choose category", docsUrl: "/docs/2" },
  { step: 3, title: "Publish", description: "Go live", docsUrl: "/docs/3" },
];

describe("GettingStartedGuide", () => {
  it("shows all steps", () => {
    const { container } = render(<GettingStartedGuide steps={STEPS} completedSteps={[]} />);
    expect(container.textContent).toContain("Create Account");
    expect(container.textContent).toContain("Publish");
  });
  it("shows progress", () => {
    const { container } = render(<GettingStartedGuide steps={STEPS} completedSteps={[1, 2]} />);
    expect(container.textContent).toContain("67%");
  });
  it("marks completed", () => {
    const { container } = render(<GettingStartedGuide steps={STEPS} completedSteps={[1]} />);
    expect(container.textContent).toContain("✓");
  });
});
