import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiPlaygroundLayout } from "@/components/api-playground-layout";

describe("ApiPlaygroundLayout", () => {
  it("renders", () => {
    const { container } = render(
      <ApiPlaygroundLayout collections={[{ name: "Auth" }]} environments={[{ name: "prod" }, { name: "dev" }]}
        activeEnv="prod" onEnvChange={vi.fn()}>
        <p>Request builder</p>
      </ApiPlaygroundLayout>
    );
    expect(container.textContent).toContain("Auth");
    expect(container.textContent).toContain("Request builder");
    expect(container.querySelector("select")).toBeTruthy();
  });
});
