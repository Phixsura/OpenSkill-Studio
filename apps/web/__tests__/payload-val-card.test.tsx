import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PayloadValCard } from "@/components/payload-val-card";

describe("PayloadValCard", () => {
  it("renders", () => {
    const { container } = render(
      <PayloadValCard valid={false} errorCount={2} fieldsChecked={3}
        errors={[
          { field: "name", error: "required" },
          { field: "age", error: "min_value_0" },
        ]} />
    );
    expect(container.textContent).toContain("Payload Validation");
    expect(container.textContent).toContain("3 fields");
    expect(container.textContent).toContain("2 errors");
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("required");
  });
});
