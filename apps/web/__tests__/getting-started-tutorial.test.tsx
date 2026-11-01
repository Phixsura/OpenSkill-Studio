import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GettingStartedTutorial } from "@/components/getting-started-tutorial";

describe("GettingStartedTutorial", () => {
  const steps = [
    { step: 1, title: "Set Up", duration_min: 5, content: "Install CLI", commands: ["npm install"] },
    { step: 2, title: "Create App", duration_min: 10, content: "Scaffold", commands: ["openskill create"] },
  ];
  it("renders", () => {
    const { container } = render(<GettingStartedTutorial steps={steps} completedSteps={[]} onCompleteStep={vi.fn()} />);
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("0%");
    expect(container.textContent).toContain("Set Up");
    expect(container.textContent).toContain("npm install");
  });
  it("marks complete", () => {
    const fn = vi.fn();
    const { container } = render(<GettingStartedTutorial steps={steps} completedSteps={[]} onCompleteStep={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Mark Complete")!);
    expect(fn).toHaveBeenCalledWith(1);
  });
  it("shows progress", () => {
    const { container } = render(<GettingStartedTutorial steps={steps} completedSteps={[1]} onCompleteStep={vi.fn()} />);
    expect(container.textContent).toContain("50%");
  });
});
