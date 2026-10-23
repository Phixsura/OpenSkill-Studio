import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppScaffoldWizard } from "@/components/app-scaffold-wizard";

describe("AppScaffoldWizard", () => {
  const files = [
    { path: "package.json", type: "config" },
    { path: "src/index.ts", type: "source" },
    { path: "tests/index.test.ts", type: "test" },
  ];
  it("renders scaffold", () => {
    const { container } = render(
      <AppScaffoldWizard files={files} appName="my-app" runtime="node" features={["tests"]} onGenerate={vi.fn()} />
    );
    expect(container.textContent).toContain("my-app");
    expect(container.textContent).toContain("package.json");
    expect(container.textContent).toContain("src/index.ts");
    expect(container.textContent).toContain("Generate");
  });
  it("generate click", () => {
    const fn = vi.fn();
    const { container } = render(
      <AppScaffoldWizard files={files} appName="x" runtime="node" features={[]} onGenerate={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
