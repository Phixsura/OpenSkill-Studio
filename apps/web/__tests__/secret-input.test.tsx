import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SecretInput } from "@/components/secret-input";

describe("SecretInput", () => {
  it("renders label", () => {
    const { container } = render(<SecretInput label="API Key" name="api_key" onSave={vi.fn()} />);
    expect(container.textContent).toContain("API Key");
  });

  it("renders required marker", () => {
    const { container } = render(<SecretInput label="Key" name="k" required onSave={vi.fn()} />);
    expect(container.textContent).toContain("*");
  });

  it("shows saved indicator", () => {
    const { container } = render(<SecretInput label="Key" name="k" onSave={vi.fn()} saved />);
    expect(container.textContent).toContain("Saved");
  });

  it("has password input by default", () => {
    const { container } = render(<SecretInput label="Key" name="k" onSave={vi.fn()} />);
    const input = container.querySelector("input");
    expect(input?.type).toBe("password");
  });

  it("has show/hide toggle", () => {
    const { container } = render(<SecretInput label="Key" name="k" onSave={vi.fn()} />);
    expect(container.textContent).toContain("Show");
  });

  it("has save button", () => {
    const { container } = render(<SecretInput label="Key" name="k" onSave={vi.fn()} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Save");
    expect(btn).toBeTruthy();
  });

  it("shows description", () => {
    const { container } = render(<SecretInput label="Key" name="k" description="Your API key" onSave={vi.fn()} />);
    expect(container.textContent).toContain("Your API key");
  });
});
