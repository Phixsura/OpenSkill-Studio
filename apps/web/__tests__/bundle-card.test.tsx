import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BundleCard } from "@/components/bundle-card";

const bundle = { bundleId: "bnd-1", name: "Starter Pack", description: "Essential tools", extensions: ["auth", "analytics", "ui-kit"], discountPct: 20, installCount: 150 };

describe("BundleCard", () => {
  it("renders bundle", () => {
    const { container } = render(<BundleCard bundle={bundle} />);
    expect(container.textContent).toContain("Starter Pack");
    expect(container.textContent).toContain("-20%");
    expect(container.textContent).toContain("3 extensions");
  });
  it("install action", () => {
    const fn = vi.fn();
    const { container } = render(<BundleCard bundle={bundle} onInstall={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("bnd-1");
  });
});
