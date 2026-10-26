import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorCodeReference } from "@/components/error-code-reference";
const codes = [{ code: "EXT_NOT_FOUND", message: "Not found", httpStatus: 404, category: "extension" }];
describe("ErrorCodeReference", () => {
  it("renders", () => {
    const { container } = render(<ErrorCodeReference codes={codes} />);
    expect(container.textContent).toContain("EXT_NOT_FOUND");
    expect(container.textContent).toContain("404");
  });
});
