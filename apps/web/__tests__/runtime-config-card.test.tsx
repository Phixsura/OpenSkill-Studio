import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RuntimeConfigCard from "../src/components/runtime-config-card";

const values = { debug: true, timeout: 30, api_key: "sk_live_xxx" };
const history = [
  {
    version: 3,
    changed_by: "admin",
    timestamp: new Date(Date.now() - 60000).toISOString(),
    key_count: 3,
  },
  {
    version: 2,
    changed_by: "system",
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    key_count: 2,
  },
];

describe("RuntimeConfigCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <RuntimeConfigCard currentValues={values} history={history} appName="My App" />,
    );
    expect(container.textContent).toContain("Runtime Config");
    expect(container.textContent).toContain("My App");
  });

  it("shows current version and key count", () => {
    const { container } = render(
      <RuntimeConfigCard currentValues={values} history={history} appName="App" />,
    );
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("3 keys");
  });

  it("renders config values", () => {
    const { container } = render(
      <RuntimeConfigCard currentValues={values} history={history} appName="App" />,
    );
    expect(container.textContent).toContain("debug");
    expect(container.textContent).toContain("true");
    expect(container.textContent).toContain("timeout");
    expect(container.textContent).toContain("30");
  });

  it("shows version history", () => {
    const { container } = render(
      <RuntimeConfigCard currentValues={values} history={history} appName="App" />,
    );
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("system");
  });

  it("shows empty state", () => {
    const { container } = render(
      <RuntimeConfigCard currentValues={{}} history={[]} appName="App" />,
    );
    expect(container.textContent).toContain("No configuration");
  });
});
