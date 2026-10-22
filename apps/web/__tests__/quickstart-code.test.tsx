import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QuickstartCode } from "@/components/quickstart-code";

describe("QuickstartCode", () => {
  it("shows Python by default", () => {
    const { container } = render(<QuickstartCode pythonCode="import sdk" typescriptCode="import {}" />);
    expect(container.textContent).toContain("import sdk");
  });
  it("has language tabs", () => {
    const { container } = render(<QuickstartCode pythonCode="py" typescriptCode="ts" />);
    expect(container.textContent).toContain("Python");
    expect(container.textContent).toContain("TypeScript");
  });
});
