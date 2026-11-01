import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ConfigDriftCard from "../src/components/config-drift-card";

const report = {
  source_env: "staging",
  target_env: "prod",
  drifts: [
    {
      key: "DB_HOST",
      drift_type: "changed" as const,
      source_value: "staging-db",
      target_value: "prod-db",
    },
    {
      key: "SENTRY_DSN",
      drift_type: "added" as const,
      source_value: null,
      target_value: "https://sentry",
    },
    { key: "DEBUG", drift_type: "removed" as const, source_value: "true", target_value: null },
  ],
};

describe("ConfigDriftCard", () => {
  it("renders header and env count", () => {
    const { container } = render(
      <ConfigDriftCard report={report} environments={["staging", "prod"]} appName="App" />,
    );
    expect(container.textContent).toContain("Config Drift");
    expect(container.textContent).toContain("2 envs");
  });

  it("shows env comparison", () => {
    const { container } = render(
      <ConfigDriftCard report={report} environments={["staging", "prod"]} appName="App" />,
    );
    expect(container.textContent).toContain("staging");
    expect(container.textContent).toContain("prod");
  });

  it("shows drift keys and types", () => {
    const { container } = render(
      <ConfigDriftCard report={report} environments={[]} appName="App" />,
    );
    expect(container.textContent).toContain("DB_HOST");
    expect(container.textContent).toContain("changed");
    expect(container.textContent).toContain("SENTRY_DSN");
    expect(container.textContent).toContain("added");
    expect(container.textContent).toContain("removed");
  });

  it("shows difference count", () => {
    const { container } = render(
      <ConfigDriftCard report={report} environments={[]} appName="App" />,
    );
    expect(container.textContent).toContain("3 differences");
  });

  it("shows no report state", () => {
    const { container } = render(<ConfigDriftCard report={null} environments={[]} appName="App" />);
    expect(container.textContent).toContain("No drift report");
  });

  it("shows no drift message", () => {
    const clean = { source_env: "a", target_env: "b", drifts: [] };
    const { container } = render(
      <ConfigDriftCard report={clean} environments={["a", "b"]} appName="App" />,
    );
    expect(container.textContent).toContain("No drift detected");
  });
});
