import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorCodeReference } from "@/components/error-code-reference";

const ERRORS = [
  { code: "APP_NOT_FOUND", status: 404, message: "App not found" },
  { code: "RATE_LIMITED", status: 429, message: "Rate limit exceeded" },
];

describe("ErrorCodeReference", () => {
  it("renders table", () => {
    const { container } = render(<ErrorCodeReference errors={ERRORS} />);
    expect(container.querySelector("table")).toBeTruthy();
  });

  it("shows error codes", () => {
    const { container } = render(<ErrorCodeReference errors={ERRORS} />);
    expect(container.textContent).toContain("APP_NOT_FOUND");
    expect(container.textContent).toContain("RATE_LIMITED");
  });

  it("shows status codes", () => {
    const { container } = render(<ErrorCodeReference errors={ERRORS} />);
    expect(container.textContent).toContain("404");
    expect(container.textContent).toContain("429");
  });

  it("returns null for empty", () => {
    const { container } = render(<ErrorCodeReference errors={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
