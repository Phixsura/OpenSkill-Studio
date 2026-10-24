import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TransferDialog } from "@/components/transfer-dialog";

describe("TransferDialog", () => {
  it("renders form", () => {
    const { container } = render(<TransferDialog appName="MyApp" onSubmit={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("Transfer MyApp");
    expect(container.querySelectorAll("input").length).toBe(2);
  });
  it("disabled without target", () => {
    const { container } = render(<TransferDialog appName="X" onSubmit={vi.fn()} onCancel={vi.fn()} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Transfer") as HTMLButtonElement;
    expect(btn.disabled).toBe(true);
  });
});
