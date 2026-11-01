import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CliToolManager } from "@/components/cli-tool-manager";

describe("CliToolManager", () => {
  it("renders tools", () => {
    const { container } = render(
      <CliToolManager installed={2} outdated={1} onInstall={vi.fn()} onUpdate={vi.fn()}
        tools={[
          { name: "node", current: "18.0.0", latest: "20.0.0", installed: true, updateAvailable: true },
          { name: "docker", current: "24.0", latest: "24.0", installed: true, updateAvailable: false },
          { name: "kubectl", current: "", latest: "1.28", installed: false, updateAvailable: false },
        ]} />
    );
    expect(container.textContent).toContain("CLI Tools");
    expect(container.textContent).toContain("2 installed");
    expect(container.textContent).toContain("1 outdated");
    expect(container.textContent).toContain("node");
    expect(container.textContent).toContain("v20.0.0");
    expect(container.textContent).toContain("Update");
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("Current");
  });
});
