import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EnvConfigEditor } from "@/components/env-config-editor";
describe("EnvConfigEditor", () => {
  it("renders vars", () => {
    const { container } = render(<EnvConfigEditor variables={[{ key: "PORT", value: "3000", secret: false }]} secretCount={0} />);
    expect(container.textContent).toContain("PORT");
    expect(container.textContent).toContain("3000");
  });
});
