import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlaygroundSandboxLauncher } from "@/components/playground-sandbox-launcher";

describe("PlaygroundSandboxLauncher", () => {
  it("renders", () => {
    const { container } = render(
      <PlaygroundSandboxLauncher appName="MyApp" templates={["react", "node", "python"]}
        onLaunch={vi.fn()} activeSandboxes={1} maxConcurrent={3} />
    );
    expect(container.textContent).toContain("Try MyApp");
    expect(container.textContent).toContain("1/3");
    expect(container.textContent).toContain("react");
    expect(container.textContent).toContain("⚛️");
  });
  it("launch", () => {
    const fn = vi.fn();
    const { container } = render(
      <PlaygroundSandboxLauncher appName="App" templates={["react"]}
        onLaunch={fn} activeSandboxes={0} maxConcurrent={3} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Launch"))!);
    expect(fn).toHaveBeenCalledWith("react");
  });
});
