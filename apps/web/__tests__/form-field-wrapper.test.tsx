import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FormFieldWrapper } from "@/components/form-field-wrapper";

describe("FormFieldWrapper", () => {
  it("renders label", () => {
    const { container } = render(
      <FormFieldWrapper label="Email" required><input /></FormFieldWrapper>
    );
    expect(container.textContent).toContain("Email");
    expect(container.textContent).toContain("*");
  });
  it("shows error", () => {
    const { container } = render(
      <FormFieldWrapper label="Name" error="Required"><input /></FormFieldWrapper>
    );
    expect(container.textContent).toContain("Required");
  });
  it("shows hint", () => {
    const { container } = render(
      <FormFieldWrapper label="Slug" hint="URL-safe identifier"><input /></FormFieldWrapper>
    );
    expect(container.textContent).toContain("URL-safe");
  });
  it("error overrides hint", () => {
    const { container } = render(
      <FormFieldWrapper label="X" error="Bad" hint="Help"><input /></FormFieldWrapper>
    );
    expect(container.textContent).toContain("Bad");
    expect(container.textContent).not.toContain("Help");
  });
});
