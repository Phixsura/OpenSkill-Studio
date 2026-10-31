import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CLIScaffoldPanel } from "@/components/cli-scaffold-panel";

const mockResult = {
  extensionName: "my-ext",
  runtime: "node20",
  files: [
    { path: "manifest.json", size: 250, isEntrypoint: false },
    { path: "src/index.ts", size: 180, isEntrypoint: true },
    { path: "package.json", size: 120, isEntrypoint: false },
    { path: "README.md", size: 300, isEntrypoint: false },
  ],
};

describe("CLIScaffoldPanel", () => {
  it("renders scaffold form", () => {
    const { container } = render(<CLIScaffoldPanel result={null} />);
    expect(container.textContent).toContain("Scaffold Extension");
    expect(container.textContent).toContain("Node.js 20");
    expect(container.textContent).toContain("Python 3.12");
  });

  it("calls onGenerate", () => {
    const onGenerate = vi.fn();
    const { getByText, getByPlaceholderText } = render(
      <CLIScaffoldPanel result={null} onGenerate={onGenerate} />
    );
    fireEvent.change(getByPlaceholderText("my-awesome-extension"), { target: { value: "test-ext" } });
    fireEvent.click(getByText("Generate Project"));
    expect(onGenerate).toHaveBeenCalledWith("test-ext", "node20");
  });

  it("shows generated files", () => {
    const { container } = render(<CLIScaffoldPanel result={mockResult} />);
    expect(container.textContent).toContain("manifest.json");
    expect(container.textContent).toContain("src/index.ts");
    expect(container.textContent).toContain("my-ext");
  });

  it("calls onDownload", () => {
    const onDownload = vi.fn();
    const { getByText } = render(<CLIScaffoldPanel result={mockResult} onDownload={onDownload} />);
    fireEvent.click(getByText("Download ZIP"));
    expect(onDownload).toHaveBeenCalled();
  });
});
