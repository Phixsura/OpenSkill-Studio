import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigValidatorPanel } from "@/components/config-validator-panel";

describe("ConfigValidatorPanel", () => {
  it("renders valid result", () => {
    const result = { valid: true, issues: [] };
    const { container } = render(<ConfigValidatorPanel result={result} />);
    expect(container.textContent).toContain("Valid configuration");
  });
  it("renders invalid result", () => {
    const result = { valid: false, issues: ["Missing required field: name", "[warn] Unknown field: foo"] };
    const { container } = render(<ConfigValidatorPanel result={result} />);
    expect(container.textContent).toContain("Invalid configuration");
    expect(container.textContent).toContain("Missing required field: name");
  });
  it("renders empty state", () => {
    const { container } = render(<ConfigValidatorPanel result={null} />);
    expect(container.querySelector("textarea")).toBeTruthy();
  });
});
