import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxQuotaCard } from "@/components/sandbox-quota-card";

const quota = { tier: "free", activeSandboxes: 2, maxSandboxes: 3, memoryUsedMb: 128, maxMemoryMb: 256 };

describe("SandboxQuotaCard", () => {
  it("renders quota info", () => {
    const { container } = render(<SandboxQuotaCard quota={quota} />);
    expect(container.textContent).toContain("2/3");
    expect(container.textContent).toContain("128MB/256MB");
    expect(container.textContent).toContain("free");
  });
  it("upgrade button works", () => {
    const fn = vi.fn();
    const { container } = render(<SandboxQuotaCard quota={quota} onUpgrade={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
