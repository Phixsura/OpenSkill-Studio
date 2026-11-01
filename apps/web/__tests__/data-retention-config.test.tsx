import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataRetentionConfig } from "@/components/data-retention-config";

describe("DataRetentionConfig", () => {
  it("renders config", () => {
    const onPreset = vi.fn();
    const { container, getByText } = render(
      <DataRetentionConfig currentPreset="standard" onPreset={onPreset}
        presets={[{ id: "minimal", label: "Minimal", maxDays: 90 }, { id: "standard", label: "Standard", maxDays: 365 }]}
        config={{ logs: 30, analytics: 90, user_data: 365 }} />
    );
    expect(container.textContent).toContain("Data Retention");
    expect(container.textContent).toContain("30 days");
    expect(container.textContent).toContain("365 days");
    fireEvent.click(getByText("Minimal"));
    expect(onPreset).toHaveBeenCalledWith("minimal");
  });
});
