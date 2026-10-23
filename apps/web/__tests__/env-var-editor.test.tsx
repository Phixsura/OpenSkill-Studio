import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvVarEditor } from "@/components/env-var-editor";

describe("EnvVarEditor", () => {
  it("renders vars", () => {
    const { container } = render(
      <EnvVarEditor onSet={vi.fn()} onDelete={vi.fn()} vars={[
        { key: "APP_NAME", value: "myapp", secret: false },
        { key: "API_SECRET", value: "••••••••", secret: true },
      ]} />
    );
    expect(container.textContent).toContain("Environment Variables");
    expect(container.textContent).toContain("2 vars");
    expect(container.textContent).toContain("APP_NAME");
    expect(container.textContent).toContain("myapp");
    expect(container.textContent).toContain("••••••••");
    expect(container.textContent).toContain("Add Variable");
  });
});
