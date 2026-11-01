import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RoleAssignmentForm } from "@/components/role-assignment-form";

describe("RoleAssignmentForm", () => {
  it("renders form", () => {
    const { container } = render(<RoleAssignmentForm onAssign={vi.fn()} />);
    expect(container.textContent).toContain("Add Team Member");
    expect(container.querySelector("input")).toBeTruthy();
    expect(container.querySelector("select")).toBeTruthy();
  });
  it("disabled without user", () => {
    const { container } = render(<RoleAssignmentForm onAssign={vi.fn()} />);
    const btn = container.querySelector("button") as HTMLButtonElement;
    expect(btn.disabled).toBe(true);
  });
  it("calls onAssign", () => {
    const fn = vi.fn();
    const { container } = render(<RoleAssignmentForm onAssign={fn} />);
    const input = container.querySelector("input")!;
    fireEvent.change(input, { target: { value: "user@test.com" } });
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("user@test.com", "viewer");
  });
});
