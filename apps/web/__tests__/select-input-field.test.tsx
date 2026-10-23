import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SelectInputField } from "@/components/select-input-field";

describe("SelectInputField", () => {
  const options = [
    { value: "us", label: "United States", icon: null, disabled: false },
    { value: "gb", label: "United Kingdom", icon: "🇬🇧", disabled: false },
  ];
  it("renders", () => {
    const { container } = render(
      <SelectInputField name="country" label="Country" options={options}
        placeholder="Select country" required={true} value="" error={null}
        onChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Country");
    expect(container.textContent).toContain("*");
    expect(container.textContent).toContain("Select country");
    expect(container.textContent).toContain("United States");
    expect(container.querySelector("select")).toBeTruthy();
  });
  it("change", () => {
    const fn = vi.fn();
    const { container } = render(
      <SelectInputField name="x" label="X" options={options} placeholder="..."
        required={false} value="" error={null} onChange={fn} />
    );
    fireEvent.change(container.querySelector("select")!, { target: { value: "gb" } });
    expect(fn).toHaveBeenCalledWith("gb");
  });
});
