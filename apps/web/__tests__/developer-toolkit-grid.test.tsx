import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperToolkitGrid } from "@/components/developer-toolkit-grid";

describe("DeveloperToolkitGrid", () => {
  const tools = [
    { id: "api_playground", name: "API Playground", icon: "🎮", category: "development", description: "Test APIs" },
    { id: "secret_scanner", name: "Secret Scanner", icon: "🔍", category: "security", description: "Scan secrets" },
  ];
  it("renders", () => {
    const { container } = render(
      <DeveloperToolkitGrid tools={tools} categories={["development", "security"]} onToolClick={vi.fn()} />
    );
    expect(container.textContent).toContain("🧰 Developer Toolkit");
    expect(container.textContent).toContain("2 tools");
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("🎮");
    expect(container.textContent).toContain("Secret Scanner");
  });
  it("click tool", () => {
    const fn = vi.fn();
    const { container } = render(
      <DeveloperToolkitGrid tools={tools} categories={[]} onToolClick={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("api_playground");
  });
});
