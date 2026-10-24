import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppCopyIdButton } from "@/components/app-copy-id-button";

describe("AppCopyIdButton", () => {
  it("shows label", () => {
    const { container } = render(<AppCopyIdButton id="abc123" />);
    expect(container.textContent).toContain("Copy ID");
  });

  it("custom label", () => {
    const { container } = render(<AppCopyIdButton id="x" label="Copy App ID" />);
    expect(container.textContent).toContain("Copy App ID");
  });

  it("has title with id", () => {
    const { container } = render(<AppCopyIdButton id="test-id-123" />);
    expect(container.querySelector("button")?.title).toBe("test-id-123");
  });
});
