import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ConfigOverrideCard from "../src/components/config-override-card";

const layers = [
  { layer_id: "env", priority: 10, key_count: 2 },
  { layer_id: "base", priority: 0, key_count: 3 },
];
const resolved = { debug: true, port: 8080, timeout: 30 };

describe("ConfigOverrideCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <ConfigOverrideCard layers={layers} resolved={resolved} appName="My App" />,
    );
    expect(container.textContent).toContain("Config Layers");
    expect(container.textContent).toContain("My App");
  });

  it("shows layer and key counts", () => {
    const { container } = render(
      <ConfigOverrideCard layers={layers} resolved={resolved} appName="App" />,
    );
    expect(container.textContent).toContain("2 layers");
    expect(container.textContent).toContain("3 keys");
  });

  it("renders layer chips", () => {
    const { container } = render(
      <ConfigOverrideCard layers={layers} resolved={resolved} appName="App" />,
    );
    expect(container.textContent).toContain("env (p10)");
    expect(container.textContent).toContain("base (p0)");
  });

  it("shows resolved config keys and values", () => {
    const { container } = render(
      <ConfigOverrideCard layers={layers} resolved={resolved} appName="App" />,
    );
    expect(container.textContent).toContain("debug");
    expect(container.textContent).toContain("true");
    expect(container.textContent).toContain("port");
    expect(container.textContent).toContain("8080");
  });

  it("shows empty state", () => {
    const { container } = render(<ConfigOverrideCard layers={[]} resolved={{}} appName="App" />);
    expect(container.textContent).toContain("No configuration");
  });
});
