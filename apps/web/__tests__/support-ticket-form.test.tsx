import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SupportTicketForm } from "@/components/support-ticket-form";

describe("SupportTicketForm", () => {
  it("has subject input", () => {
    const { container } = render(<SupportTicketForm onSubmit={vi.fn()} />);
    expect(container.querySelector("input")).toBeTruthy();
  });
  it("has priority select", () => {
    const { container } = render(<SupportTicketForm onSubmit={vi.fn()} />);
    expect(container.querySelectorAll("option").length).toBe(4);
  });
  it("has submit button", () => {
    const { container } = render(<SupportTicketForm onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Submit");
  });
});
