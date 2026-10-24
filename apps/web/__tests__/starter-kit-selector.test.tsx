import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StarterKitSelector } from "@/components/starter-kit-selector";

describe("StarterKitSelector", () => {
  const kits = [
    { id: "ts-basic", name: "TypeScript Basic", language: "typescript", files: ["index.ts"], dependencies: ["@openskill/sdk"] },
    { id: "py-basic", name: "Python Basic", language: "python", files: ["main.py"], dependencies: ["openskill-sdk"] },
  ];
  it("renders kits", () => {
    const { container } = render(<StarterKitSelector kits={kits} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("TypeScript Basic");
    expect(container.textContent).toContain("Python Basic");
    expect(container.textContent).toContain("@openskill/sdk");
  });
  it("selects kit", () => {
    const fn = vi.fn();
    const { container } = render(<StarterKitSelector kits={kits} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("ts-basic");
  });
});
