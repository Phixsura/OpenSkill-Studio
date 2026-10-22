import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvVarEditor } from "@/components/env-var-editor";

const VARS = [{ key: "API_KEY", value: "secret" }, { key: "DB_HOST", value: "localhost" }];

describe("EnvVarEditor", () => {
  it("shows vars", () => {
    const { container } = render(<EnvVarEditor vars={VARS} onChange={vi.fn()} />);
    expect(container.textContent).toContain("API_KEY");
    expect(container.textContent).toContain("DB_HOST");
  });

  it("masks values", () => {
    const { container } = render(<EnvVarEditor vars={VARS} onChange={vi.fn()} />);
    expect(container.textContent).toContain("••••••");
    expect(container.textContent).not.toContain("secret");
  });

  it("has add form", () => {
    const { container } = render(<EnvVarEditor vars={[]} onChange={vi.fn()} />);
    expect(container.querySelectorAll("input").length).toBe(2);
    expect(container.textContent).toContain("Add");
  });

  it("has remove buttons", () => {
    const { container } = render(<EnvVarEditor vars={VARS} onChange={vi.fn()} />);
    expect(container.querySelectorAll("button").length).toBeGreaterThanOrEqual(2);
  });
});
