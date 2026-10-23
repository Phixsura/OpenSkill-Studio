import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataExportPageLayout } from "@/components/data-export-page-layout";

describe("DataExportPageLayout", () => {
  const options = [
    { id: "profile", label: "Profile", description: "Your data", icon: "👤", formats: ["json", "csv"], estimated_size_kb: 50 },
  ];
  it("renders", () => {
    const { container } = render(<DataExportPageLayout exportOptions={options} onExport={vi.fn()} />);
    expect(container.textContent).toContain("Export Your Data");
    expect(container.textContent).toContain("Profile");
    expect(container.textContent).toContain("50 KB");
  });
  it("exports", () => {
    const fn = vi.fn();
    const { container } = render(<DataExportPageLayout exportOptions={options} onExport={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "json")!);
    expect(fn).toHaveBeenCalledWith("profile", "json");
  });
});
