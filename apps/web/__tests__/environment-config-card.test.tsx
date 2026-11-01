import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EnvironmentConfigCard from "../src/components/environment-config-card";

const envs = [
  { env_id: "dev", name: "Development", setting_count: 5, locked: false },
  { env_id: "staging", name: "Staging", setting_count: 8, locked: false },
  { env_id: "prod", name: "Production", setting_count: 10, locked: true },
];

describe("EnvironmentConfigCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<EnvironmentConfigCard environments={envs} appName="My App" />);
    expect(container.textContent).toContain("Environments");
    expect(container.textContent).toContain("My App");
  });

  it("shows environment count", () => {
    const { container } = render(<EnvironmentConfigCard environments={envs} appName="App" />);
    expect(container.textContent).toContain("3 environments");
  });

  it("renders environment names", () => {
    const { container } = render(<EnvironmentConfigCard environments={envs} appName="App" />);
    expect(container.textContent).toContain("Development");
    expect(container.textContent).toContain("Staging");
    expect(container.textContent).toContain("Production");
  });

  it("shows setting counts", () => {
    const { container } = render(<EnvironmentConfigCard environments={envs} appName="App" />);
    expect(container.textContent).toContain("10 settings");
  });

  it("shows locked indicator", () => {
    const { container } = render(<EnvironmentConfigCard environments={envs} appName="App" />);
    expect(container.textContent).toContain("locked");
  });

  it("shows empty state", () => {
    const { container } = render(<EnvironmentConfigCard environments={[]} appName="App" />);
    expect(container.textContent).toContain("No environments");
  });
});
