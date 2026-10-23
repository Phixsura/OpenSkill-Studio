import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorCodeCatalog } from "@/components/error-code-catalog";

describe("ErrorCodeCatalog", () => {
  const errors = [
    { code: 1001, name: "invalid_token", message: "Bad token", httpStatus: 401, category: "AUTH", machineCode: "ERR_INVALID_TOKEN" },
    { code: 2001, name: "missing_field", message: "Field required", httpStatus: 400, category: "INPUT", machineCode: "ERR_MISSING_FIELD" },
  ];
  it("renders errors", () => {
    const { container } = render(<ErrorCodeCatalog errors={errors} categories={["AUTH", "INPUT"]} />);
    expect(container.textContent).toContain("1001");
    expect(container.textContent).toContain("ERR_INVALID_TOKEN");
    expect(container.textContent).toContain("Bad token");
  });
  it("filters by category", () => {
    const { container } = render(<ErrorCodeCatalog errors={errors} categories={["AUTH", "INPUT"]} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "AUTH")!);
    expect(container.textContent).toContain("1001");
    expect(container.textContent).not.toContain("2001");
  });
});
