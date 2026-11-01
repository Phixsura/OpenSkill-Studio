import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SdkQuickstartPage } from "@/components/sdk-quickstart-page";

describe("SdkQuickstartPage", () => {
  const steps = [
    { order: 1, title: "Install", code: "npm install @openskill/sdk" },
    { order: 2, title: "Use", code: "const apps = await client.apps.list();" },
  ];
  it("renders quickstart", () => {
    const { container } = render(
      <SdkQuickstartPage steps={steps} language="typescript"
        availableLanguages={["typescript", "python"]} onLanguageChange={vi.fn()} />
    );
    expect(container.textContent).toContain("SDK Quickstart");
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("npm install");
    expect(container.textContent).toContain("typescript");
    expect(container.textContent).toContain("python");
  });
});
