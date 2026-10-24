import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TemplatePreview } from "@/components/template-preview";

describe("TemplatePreview", () => {
  it("renders template and output", () => {
    const { container } = render(
      <TemplatePreview template="Hello, {{ name }}!" output="Hello, World!" missing={[]} hasMissing={false} />
    );
    expect(container.textContent).toContain("Hello, {{ name }}!");
    expect(container.textContent).toContain("Hello, World!");
  });
  it("shows missing vars", () => {
    const { container } = render(
      <TemplatePreview template="{{ x }}" output="{{ x }}" missing={["x"]} hasMissing={true} />
    );
    expect(container.textContent).toContain("Missing variables: x");
  });
});
