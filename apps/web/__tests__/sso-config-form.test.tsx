import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SsoConfigForm } from "@/components/sso-config-form";

describe("SsoConfigForm", () => {
  it("renders form", () => {
    const { container } = render(<SsoConfigForm onSave={vi.fn()} />);
    expect(container.textContent).toContain("SSO Configuration");
    expect(container.querySelector("select")).toBeTruthy();
    expect(container.querySelectorAll("input").length).toBe(2);
  });
  it("disabled without values", () => {
    const { container } = render(<SsoConfigForm onSave={vi.fn()} />);
    const btn = container.querySelector("button") as HTMLButtonElement;
    expect(btn.disabled).toBe(true);
  });
});
