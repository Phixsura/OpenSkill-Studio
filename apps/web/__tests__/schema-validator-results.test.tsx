import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SchemaValidatorResults } from "@/components/schema-validator-results";

describe("SchemaValidatorResults", () => {
  it("renders valid", () => {
    const { container } = render(<SchemaValidatorResults valid={true} errors={[]} errorCount={0} />);
    expect(container.textContent).toContain("Valid");
  });
  it("renders errors", () => {
    const { container } = render(
      <SchemaValidatorResults valid={false} errorCount={2} errors={[
        { path: "name", error: "required", message: "name is required" },
        { path: "age", error: "type", message: "Expected integer" },
      ]} />
    );
    expect(container.textContent).toContain("2 validation errors");
    expect(container.textContent).toContain("name is required");
    expect(container.textContent).toContain("Expected integer");
  });
});
