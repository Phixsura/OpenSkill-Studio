import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResponseValidator } from "@/components/response-validator";

describe("ResponseValidator", () => {
  it("valid response", () => {
    const { container } = render(<ResponseValidator valid={true} errors={[]} checkedFields={3} passedFields={3} />);
    expect(container.textContent).toContain("3/3 passed");
  });
  it("invalid response", () => {
    const errors = [{ field: "id", error: "Missing required field" }];
    const { container } = render(<ResponseValidator valid={false} errors={errors} checkedFields={2} passedFields={1} />);
    expect(container.textContent).toContain("1 errors");
    expect(container.textContent).toContain("id");
  });
});
