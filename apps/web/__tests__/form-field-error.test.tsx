import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FormFieldError } from "@/components/form-field-error";

describe("FormFieldError", () => {
  it("shows errors when touched", () => {
    const { container } = render(<FormFieldError errors={["Required", "Too short"]} touched={true} />);
    expect(container.textContent).toContain("Required");
    expect(container.textContent).toContain("Too short");
  });
  it("hides when not touched", () => {
    const { container } = render(<FormFieldError errors={["Required"]} touched={false} />);
    expect(container.textContent).toBe("");
  });
  it("hides when no errors", () => {
    const { container } = render(<FormFieldError errors={[]} touched={true} />);
    expect(container.textContent).toBe("");
  });
});
