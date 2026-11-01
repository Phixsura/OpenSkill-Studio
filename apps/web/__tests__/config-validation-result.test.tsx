import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigValidationResult } from "@/components/config-validation-result";

describe("ConfigValidationResult", () => {
  it("renders errors and warnings", () => {
    const { container } = render(
      <ConfigValidationResult valid={false}
        errors={[{ key: "name", error: "missing_required" }]}
        warnings={[{ key: "extra", warning: "unknown_field" }]} />
    );
    expect(container.textContent).toContain("Validation Failed");
    expect(container.textContent).toContain("1 errors");
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("missing required");
    expect(container.textContent).toContain("extra");
  });
});
