import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvConfigEditor } from "@/components/env-config-editor";

describe("EnvConfigEditor", () => {
  const vars = [
    { key: "API_KEY", display_value: "••••••••", is_secret: true },
    { key: "LOG_LEVEL", display_value: "info", is_secret: false },
  ];
  it("renders", () => {
    const { container } = render(<EnvConfigEditor variables={vars} onSave={vi.fn()} onDelete={vi.fn()} />);
    expect(container.textContent).toContain("Environment Variables");
    expect(container.textContent).toContain("API_KEY");
    expect(container.textContent).toContain("SECRET");
    expect(container.textContent).toContain("LOG_LEVEL");
  });
  it("delete", () => {
    const fn = vi.fn();
    const { container } = render(<EnvConfigEditor variables={vars} onSave={vi.fn()} onDelete={fn} />);
    const delBtns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "×");
    fireEvent.click(delBtns[0]);
    expect(fn).toHaveBeenCalledWith("API_KEY");
  });
});
