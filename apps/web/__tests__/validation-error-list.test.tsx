import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ValidationErrorList } from "@/components/validation-error-list";

describe("ValidationErrorList", () => {
  it("renders errors", () => {
    const errors = [{ field: "email", error: "required" }, { field: "name", error: "too short" }];
    const { container } = render(<ValidationErrorList errors={errors} />);
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("required");
    expect(container.textContent).toContain("too short");
  });
  it("hidden when no errors", () => {
    const { container } = render(<ValidationErrorList errors={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
