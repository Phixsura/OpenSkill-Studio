import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RadioGroup } from "@/components/radio-group";

describe("RadioGroup", () => {
  const items = [
    { value: "monthly", label: "Monthly", description: "$29/mo", icon: "📅", selected: false },
    { value: "yearly", label: "Yearly", description: "$290/yr (save 17%)", icon: "📆", selected: true },
  ];
  it("renders", () => {
    const { container } = render(<RadioGroup name="billing" label="Billing" items={items} onChange={vi.fn()} />);
    expect(container.textContent).toContain("Billing");
    expect(container.textContent).toContain("Monthly");
    expect(container.textContent).toContain("$29/mo");
    expect(container.textContent).toContain("Yearly");
    expect(container.textContent).toContain("save 17%");
    expect(container.querySelectorAll("input[type='radio']").length).toBe(2);
  });
  it("change", () => {
    const fn = vi.fn();
    const { container } = render(<RadioGroup name="x" label="X" items={items} onChange={fn} />);
    fireEvent.click(container.querySelectorAll("input")[0]);
    expect(fn).toHaveBeenCalledWith("monthly");
  });
});
