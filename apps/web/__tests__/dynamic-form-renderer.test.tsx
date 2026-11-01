import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DynamicFormRenderer } from "@/components/dynamic-form-renderer";

describe("DynamicFormRenderer", () => {
  const fields = [
    { name: "app_name", label: "App Name", type: "text", required: true, placeholder: "Enter name", options: [] },
    { name: "category", label: "Category", type: "select", required: false, placeholder: "", options: ["tools", "design"] },
  ];
  it("renders", () => {
    const { container } = render(<DynamicFormRenderer title="Create App" fields={fields} onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Create App");
    expect(container.textContent).toContain("App Name");
    expect(container.textContent).toContain("*");
    expect(container.querySelector("select")).toBeTruthy();
    expect(container.textContent).toContain("Submit");
  });
  it("submit", () => {
    const fn = vi.fn();
    const { container } = render(<DynamicFormRenderer title="X" fields={fields} onSubmit={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Submit")!);
    expect(fn).toHaveBeenCalled();
  });
});
