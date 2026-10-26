import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ModuleLoaderPanel } from "@/components/module-loader-panel";

const mockLog = [
  { moduleName: "json", allowed: true, reason: "Built-in allowed" },
  { moduleName: "os", allowed: false, reason: "Blocked: os is restricted" },
  { moduleName: "requests", allowed: true, reason: "Custom allowlist" },
];
const mockAllowlist = {
  builtin: ["json", "math", "re", "datetime"],
  custom: ["requests", "pandas"],
  blocked: ["os", "sys", "subprocess"],
};

describe("ModuleLoaderPanel", () => {
  it("renders import log", () => {
    const { container } = render(
      <ModuleLoaderPanel importLog={mockLog} allowlist={mockAllowlist} blockedCount={1} />
    );
    expect(container.textContent).toContain("json");
    expect(container.textContent).toContain("1 blocked");
  });

  it("shows allowed modules", () => {
    const { getByText, container } = render(
      <ModuleLoaderPanel importLog={[]} allowlist={mockAllowlist} blockedCount={0} />
    );
    fireEvent.click(getByText("Allowed"));
    expect(container.textContent).toContain("Built-in (4)");
    expect(container.textContent).toContain("requests");
  });

  it("shows blocked modules", () => {
    const { getByText, container } = render(
      <ModuleLoaderPanel importLog={[]} allowlist={mockAllowlist} blockedCount={0} />
    );
    fireEvent.click(getByText("Blocked (3)"));
    expect(container.textContent).toContain("subprocess");
  });

  it("calls onTestImport", () => {
    const onTest = vi.fn();
    const { getByText, getByPlaceholderText } = render(
      <ModuleLoaderPanel importLog={[]} allowlist={mockAllowlist} blockedCount={0} onTestImport={onTest} />
    );
    fireEvent.change(getByPlaceholderText("Test module import..."), { target: { value: "numpy" } });
    fireEvent.click(getByText("Test"));
    expect(onTest).toHaveBeenCalledWith("numpy");
  });
});
