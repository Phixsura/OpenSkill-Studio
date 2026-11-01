import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KeyExpiryAlert } from "@/components/key-expiry-alert";

describe("KeyExpiryAlert", () => {
  it("renders alert", () => {
    const onRotate = vi.fn();
    const { container, getAllByText } = render(
      <KeyExpiryAlert message="⚠️ 1 expiring" needsAction={true} onRotate={onRotate}
        expired={[]} expiring={[{ name: "staging", daysUntilExpiry: 5, status: "expiring" }]} />
    );
    expect(container.textContent).toContain("1 expiring");
    expect(container.textContent).toContain("staging");
    expect(container.textContent).toContain("5d left");
    fireEvent.click(getAllByText("Rotate")[0]);
    expect(onRotate).toHaveBeenCalledWith("staging");
  });
});
