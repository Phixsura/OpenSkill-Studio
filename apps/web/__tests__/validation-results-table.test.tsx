import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ValidationResultsTable } from "@/components/validation-results-table";

describe("ValidationResultsTable", () => {
  it("renders results", () => {
    const { container } = render(
      <ValidationResultsTable total={10} valid={8} invalid={2} passRate={80}
        errors={[
          { field: "email", rule: "required", message: "email is required" },
          { field: "age", rule: "min", message: "age below minimum 0" },
        ]} />
    );
    expect(container.textContent).toContain("Data Validation");
    expect(container.textContent).toContain("8 valid");
    expect(container.textContent).toContain("2 invalid");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("email is required");
  });
});
