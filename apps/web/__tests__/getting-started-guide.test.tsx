import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GettingStartedGuide } from "@/components/getting-started-guide";

describe("GettingStartedGuide", () => {
  const steps = [
    { order: 1, title: "Install the SDK", code: "npm install @openskill/sdk" },
    { order: 2, title: "Set API key", code: "export OSK_API_KEY=key" },
  ];
  it("renders guide", () => {
    const { container } = render(
      <GettingStartedGuide steps={steps} availableLanguages={["typescript", "python"]}
        language="typescript" onLanguageChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("Install the SDK");
    expect(container.textContent).toContain("npm install");
    expect(container.textContent).toContain("typescript");
    expect(container.textContent).toContain("python");
  });
});
