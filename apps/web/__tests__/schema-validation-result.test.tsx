import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SchemaValidationResult } from "@/components/schema-validation-result";

describe("SchemaValidationResult", () => {
  it("valid", () => {
    const { container } = render(<SchemaValidationResult valid={true} errors={[]} onFix={vi.fn()} />);
    expect(container.textContent).toContain("✅ Valid");
    expect(container.textContent).toContain("All fields pass");
  });
  it("errors", () => {
    const errors = [{ field: "email", error: "Required" }];
    const fn = vi.fn();
    const { container } = render(<SchemaValidationResult valid={false} errors={errors} onFix={fn} />);
    expect(container.textContent).toContain("❌ 1 errors");
    expect(container.textContent).toContain("email");
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Fix")!);
    expect(fn).toHaveBeenCalledWith("email");
  });
});
