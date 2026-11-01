import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TransferOwnership } from "@/components/transfer-ownership";

describe("TransferOwnership", () => {
  it("renders transfer form", () => {
    const { container } = render(
      <TransferOwnership appName="SuperApp" currentOrg="Acme Corp"
        onTransfer={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Transfer SuperApp");
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("Transfer");
    expect(container.textContent).toContain("Cancel");
    expect(container.querySelector("input[type='checkbox']")).toBeTruthy();
  });
});
