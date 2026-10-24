import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SigningKeyCard } from "@/components/signing-key-card";

describe("SigningKeyCard", () => {
  it("renders name", () => {
    const { container } = render(<SigningKeyCard name="Deploy Key" fingerprint="abc123" createdAt="2026-01-01" />);
    expect(container.textContent).toContain("Deploy Key");
  });

  it("shows fingerprint", () => {
    const { container } = render(<SigningKeyCard name="K" fingerprint="abc123def456" createdAt="now" />);
    expect(container.textContent).toContain("abc123def456");
  });

  it("shows delete button", () => {
    const onDelete = vi.fn();
    const { container } = render(<SigningKeyCard name="K" fingerprint="x" createdAt="now" onDelete={onDelete} />);
    const btn = container.querySelector("button");
    expect(btn?.textContent).toContain("Remove");
    fireEvent.click(btn!);
    expect(onDelete).toHaveBeenCalled();
  });

  it("hides delete when no handler", () => {
    const { container } = render(<SigningKeyCard name="K" fingerprint="x" createdAt="now" />);
    expect(container.querySelector("button")).toBeNull();
  });
});
