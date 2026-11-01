import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickstartGuideView } from "@/components/quickstart-guide-view";

describe("QuickstartGuideView", () => {
  const steps = [
    { step: 1, title: "Install", code: "npm install pkg", language: "bash" },
    { step: 2, title: "Init", code: 'const c = new Client()', language: "typescript" },
  ];
  it("renders", () => {
    const { container } = render(
      <QuickstartGuideView appName="Auth SDK" sdk="typescript" steps={steps}
        estimatedTimeMin={5} onCopy={vi.fn()} />
    );
    expect(container.textContent).toContain("Quick Start: Auth SDK");
    expect(container.textContent).toContain("typescript SDK");
    expect(container.textContent).toContain("~5 min");
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("npm install pkg");
  });
});
