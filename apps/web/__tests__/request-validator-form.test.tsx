import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RequestValidatorForm } from "@/components/request-validator-form";

describe("RequestValidatorForm", () => {
  it("renders errors", () => {
    const { container } = render(
      <RequestValidatorForm valid={false} onValidate={vi.fn()}
        errors={[
          { field: "name", error: "required", message: "name is required" },
          { field: "age", error: "type", message: "age must be an integer" },
        ]} />
    );
    expect(container.textContent).toContain("Request Validator");
    expect(container.textContent).toContain("2 validation errors");
    expect(container.textContent).toContain("name is required");
    expect(container.textContent).toContain("age must be an integer");
  });
});
