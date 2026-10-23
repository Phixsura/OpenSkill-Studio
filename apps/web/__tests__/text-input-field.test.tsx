import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TextInputField } from "@/components/text-input-field";

describe("TextInputField", () => {
  it("renders", () => {
    const { container } = render(
      <TextInputField name="email" label="Email" type="email" placeholder="you@example.com"
        required={true} value="" helpText="We'll never share your email" error={null}
        onChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Email");
    expect(container.textContent).toContain("*");
    expect(container.textContent).toContain("We'll never share");
    expect(container.querySelector("input")?.getAttribute("type")).toBe("email");
  });
  it("shows error", () => {
    const { container } = render(
      <TextInputField name="x" label="X" type="text" placeholder="" required={false}
        value="" helpText="Help" error="Required field" onChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Required field");
    expect(container.textContent).not.toContain("Help");
  });
  it("onChange", () => {
    const fn = vi.fn();
    const { container } = render(
      <TextInputField name="x" label="X" type="text" placeholder="" required={false}
        value="" helpText={null} error={null} onChange={fn} />
    );
    fireEvent.change(container.querySelector("input")!, { target: { value: "hello" } });
    expect(fn).toHaveBeenCalledWith("hello");
  });
});
