import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TemplatePickerGrid } from "@/components/template-picker-grid";

const TEMPLATES = [
  { id: "lms", name: "LMS Connector", category: "connector", description: "Connect LMS" },
  { id: "bot", name: "Auto Grader", category: "automation", description: "Grade automatically" },
];

describe("TemplatePickerGrid", () => {
  it("shows templates", () => {
    const { container } = render(<TemplatePickerGrid templates={TEMPLATES} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("LMS Connector");
    expect(container.textContent).toContain("Auto Grader");
  });
  it("calls onSelect", () => {
    const onSelect = vi.fn();
    const { container } = render(<TemplatePickerGrid templates={TEMPLATES} onSelect={onSelect} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(onSelect).toHaveBeenCalledWith("lms");
  });
  it("shows categories", () => {
    const { container } = render(<TemplatePickerGrid templates={TEMPLATES} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("connector");
  });
});
