import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StatusPageSubscribe } from "@/components/status-page-subscribe";

describe("StatusPageSubscribe", () => {
  it("renders options", () => {
    const { container } = render(<StatusPageSubscribe options={["email", "slack"]} onSubscribe={vi.fn()} />);
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("slack");
    expect(container.textContent).toContain("Subscribe to Updates");
  });
  it("disabled without contact", () => {
    const { container } = render(<StatusPageSubscribe options={["email"]} onSubscribe={vi.fn()} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Subscribe") as HTMLButtonElement;
    expect(btn.disabled).toBe(true);
  });
});
