import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataValidationForm } from "@/components/data-validation-form";

describe("DataValidationForm", () => {
  const results = [
    { field: "", value: "a@b.com", format: "email", valid: true, error: null },
    { field: "", value: "bad", format: "email", valid: false, error: "Does not match" },
  ];
  it("renders", () => {
    const { container } = render(
      <DataValidationForm results={results} allValid={false} onValidate={vi.fn()} />
    );
    expect(container.textContent).toContain("Data Validator");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("❌");
    expect(container.textContent).toContain("a@b.com");
    expect(container.querySelector("select")).toBeTruthy();
  });
});
