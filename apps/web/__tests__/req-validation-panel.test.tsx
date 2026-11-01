import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqValidationPanel } from "@/components/req-validation-panel";

describe("ReqValidationPanel", () => {
  it("renders errors", () => {
    const { container } = render(
      <ReqValidationPanel valid={false} fieldCount={3}
        errors={[
          { field: "name", error: "required" },
          { field: "email", error: "invalid_email" },
        ]} />
    );
    expect(container.textContent).toContain("Validation Errors");
    expect(container.textContent).toContain("3 fields checked");
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("required");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("invalid email");
  });
});
