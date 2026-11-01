import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppActionMenu } from "@/components/app-action-menu";

describe("AppActionMenu", () => {
  it("shows Actions button", () => {
    const { container } = render(<AppActionMenu appStatus="draft" onEdit={vi.fn()} />);
    expect(container.textContent).toContain("Actions");
  });

  it("shows edit on click", () => {
    const { container } = render(<AppActionMenu appStatus="draft" onEdit={vi.fn()} />);
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("Edit");
  });

  it("shows submit for draft", () => {
    const { container } = render(<AppActionMenu appStatus="draft" onSubmitReview={vi.fn()} />);
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("Submit for Review");
  });

  it("shows publish for approved", () => {
    const { container } = render(<AppActionMenu appStatus="approved" onPublish={vi.fn()} />);
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("Publish");
  });

  it("returns null when no actions", () => {
    const { container } = render(<AppActionMenu appStatus="revoked" />);
    expect(container.innerHTML).toBe("");
  });
});
