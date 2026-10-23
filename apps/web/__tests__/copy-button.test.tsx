import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CopyButton } from "@/components/copy-button";

describe("CopyButton", () => {
  it("renders button variant", () => {
    const { container } = render(<CopyButton text="hello" label="Copy Code" />);
    expect(container.textContent).toContain("Copy Code");
  });
  it("renders icon variant", () => {
    const { container } = render(<CopyButton text="hello" variant="icon" />);
    expect(container.textContent).toContain("📋");
  });
  it("shows copied state", () => {
    const { container } = render(<CopyButton text="test" />);
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("Copied! ✓");
  });
});
