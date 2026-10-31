import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EnvVariableCard from "../src/components/env-variable-card";

const variables = [
  { key: "API_KEY", value: "se********56", sensitive: true, environment: "production" },
  { key: "APP_NAME", value: "myapp", sensitive: false, environment: "production" },
];

describe("EnvVariableCard", () => {
  it("renders header and counts", () => {
    const { container } = render(
      <EnvVariableCard variables={variables} environments={["production"]} appName="App" />,
    );
    expect(container.textContent).toContain("Environment Variables");
    expect(container.textContent).toContain("2 vars");
    expect(container.textContent).toContain("1 envs");
  });

  it("shows keys and values", () => {
    const { container } = render(
      <EnvVariableCard variables={variables} environments={["production"]} appName="App" />,
    );
    expect(container.textContent).toContain("API_KEY");
    expect(container.textContent).toContain("myapp");
  });

  it("shows environment labels", () => {
    const { container } = render(
      <EnvVariableCard variables={variables} environments={["production"]} appName="App" />,
    );
    expect(container.textContent).toContain("production");
  });

  it("shows empty state", () => {
    const { container } = render(
      <EnvVariableCard variables={[]} environments={[]} appName="App" />,
    );
    expect(container.textContent).toContain("No variables");
  });
});
