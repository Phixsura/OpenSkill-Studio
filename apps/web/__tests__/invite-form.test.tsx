import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InviteForm } from "@/components/invite-form";

describe("InviteForm", () => {
  it("has email input", () => {
    const { container } = render(<InviteForm onInvite={vi.fn()} />);
    expect(container.querySelector("input[type='email']")).toBeTruthy();
  });
  it("has role select", () => {
    const { container } = render(<InviteForm onInvite={vi.fn()} />);
    expect(container.querySelector("select")).toBeTruthy();
  });
  it("has invite button", () => {
    const { container } = render(<InviteForm onInvite={vi.fn()} />);
    expect(container.textContent).toContain("Invite");
  });
  it("has role options", () => {
    const { container } = render(<InviteForm onInvite={vi.fn()} />);
    expect(container.querySelectorAll("option").length).toBe(2);
  });
});
