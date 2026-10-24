import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CopyDisplay } from "@/components/copy-display";

describe("CopyDisplay", () => {
  it("renders text", () => {
    const { container } = render(<CopyDisplay text="Install App" />);
    expect(container.textContent).toContain("Install App");
  });
  it("error variant", () => {
    const { container } = render(<CopyDisplay text="Error occurred" variant="error" />);
    expect(container.textContent).toContain("Error occurred");
    expect(container.querySelector("[class*='text-red']")).toBeTruthy();
  });
  it("success variant", () => {
    const { container } = render(<CopyDisplay text="Saved!" variant="success" />);
    expect(container.querySelector("[class*='text-green']")).toBeTruthy();
  });
});
