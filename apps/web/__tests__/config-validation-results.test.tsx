import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigValidationResults } from "@/components/config-validation-results";

describe("ConfigValidationResults", () => {
  it("valid", () => {
    const { container } = render(
      <ConfigValidationResults valid={true} errors={[]} warnings={[]} fieldsPresent={5} fieldsRequired={5} />
    );
    expect(container.textContent).toContain("✅ Valid");
    expect(container.textContent).toContain("5/5");
  });
  it("invalid with errors", () => {
    const errors = [{ field: "version", message: "Invalid semver" }];
    const warnings = [{ field: "icon", message: "No icon" }];
    const { container } = render(
      <ConfigValidationResults valid={false} errors={errors} warnings={warnings} fieldsPresent={3} fieldsRequired={5} />
    );
    expect(container.textContent).toContain("❌ Invalid");
    expect(container.textContent).toContain("Invalid semver");
    expect(container.textContent).toContain("No icon");
  });
});
