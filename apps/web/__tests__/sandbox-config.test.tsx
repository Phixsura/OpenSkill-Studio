import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxConfig } from "@/components/sandbox-config";

describe("SandboxConfig", () => {
  const runtimes = [
    { id: "node20", label: "Node.js 20", icon: "🟢" },
    { id: "python312", label: "Python 3.12", icon: "🐍" },
  ];
  it("renders runtimes", () => {
    const { container } = render(
      <SandboxConfig runtimes={runtimes} selectedRuntime="node20" memoryMb={256} timeoutS={30} onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Node.js 20");
    expect(container.textContent).toContain("Python 3.12");
    expect(container.textContent).toContain("256MB");
    expect(container.textContent).toContain("30s");
  });
  it("select runtime", () => {
    const fn = vi.fn();
    const { container } = render(
      <SandboxConfig runtimes={runtimes} selectedRuntime="" memoryMb={256} timeoutS={30} onSelect={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("python312");
  });
});
