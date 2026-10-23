import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataRetentionConfig } from "@/components/data-retention-config";

describe("DataRetentionConfig", () => {
  it("renders presets", () => {
    const { container } = render(<DataRetentionConfig activePreset="standard" onSave={vi.fn()} />);
    expect(container.textContent).toContain("minimal");
    expect(container.textContent).toContain("gdpr compliant");
    expect(container.textContent).toContain("extended");
  });
  it("saves", () => {
    const fn = vi.fn();
    const { container } = render(<DataRetentionConfig activePreset="standard" onSave={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Apply"))!);
    expect(fn).toHaveBeenCalledWith("standard");
  });
});
