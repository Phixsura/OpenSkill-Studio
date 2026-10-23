import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvVarEditor } from "@/components/env-var-editor";

describe("EnvVarEditor", () => {
  const vars = [
    { key: "DATABASE_URL", value: "postgres://localhost", is_sensitive: false, source: "manual" },
    { key: "API_KEY", value: "sk••••••", is_sensitive: true, source: "manual" },
  ];
  it("renders vars with masking", () => {
    const { container } = render(<EnvVarEditor variables={vars} onDelete={vi.fn()} />);
    expect(container.textContent).toContain("DATABASE_URL");
    expect(container.textContent).toContain("API_KEY");
    expect(container.textContent).toContain("••••••••");
  });
  it("delete click", () => {
    const fn = vi.fn();
    const { container } = render(<EnvVarEditor variables={vars} onDelete={fn} />);
    const delBtns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "Delete");
    fireEvent.click(delBtns[0]);
    expect(fn).toHaveBeenCalledWith("DATABASE_URL");
  });
});
