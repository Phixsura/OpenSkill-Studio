import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxFileExplorer } from "@/components/sandbox-file-explorer";

const mockEntries = [
  { name: "src", type: "directory" as const, size: 0, path: "/src" },
  { name: "index.js", type: "file" as const, size: 2048, path: "/index.js" },
  { name: "config.json", type: "file" as const, size: 512, path: "/config.json" },
];
const mockUsage = { usedBytes: 5242880, maxBytes: 104857600, usagePercent: 5.0 };

describe("SandboxFileExplorer", () => {
  it("renders files and directories", () => {
    const { container } = render(
      <SandboxFileExplorer entries={mockEntries} currentPath="/" usage={mockUsage} />
    );
    expect(container.textContent).toContain("src");
    expect(container.textContent).toContain("index.js");
    expect(container.textContent).toContain("2.0KB");
  });

  it("navigates to directory", () => {
    const onNav = vi.fn();
    const { getByText } = render(
      <SandboxFileExplorer entries={mockEntries} currentPath="/" usage={mockUsage} onNavigate={onNav} />
    );
    fireEvent.click(getByText("src"));
    expect(onNav).toHaveBeenCalledWith("/src");
  });

  it("shows storage usage", () => {
    const { container } = render(
      <SandboxFileExplorer entries={mockEntries} currentPath="/" usage={mockUsage} />
    );
    expect(container.textContent).toContain("5.0MB");
    expect(container.textContent).toContain("5%");
  });

  it("shows empty state", () => {
    const { container } = render(
      <SandboxFileExplorer entries={[]} currentPath="/empty" usage={mockUsage} />
    );
    expect(container.textContent).toContain("Empty directory");
  });
});
