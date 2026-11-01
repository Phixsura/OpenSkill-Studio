import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SanitizedInput } from "@/components/sanitized-input";

describe("SanitizedInput", () => {
  it("renders input", () => {
    const { container } = render(
      <SanitizedInput label="App Name" maxLength={50} placeholder="Enter name"
        onSubmit={vi.fn()} />
    );
    expect(container.textContent).toContain("App Name");
    expect(container.textContent).toContain("50 characters remaining");
    expect(container.querySelector("input")).toBeTruthy();
  });
  it("renders textarea", () => {
    const { container } = render(
      <SanitizedInput label="Description" maxLength={500} onSubmit={vi.fn()} multiline />
    );
    expect(container.querySelector("textarea")).toBeTruthy();
  });
});
