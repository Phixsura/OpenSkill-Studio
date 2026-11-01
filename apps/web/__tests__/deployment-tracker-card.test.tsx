import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DeploymentTrackerCard from "../src/components/deployment-tracker-card";

const deployed = {
  deployment_id: "dep-1",
  environment: "production",
  version: "1.2.0",
  status: "deployed" as const,
  created_at: new Date(Date.now() - 3_600_000).toISOString(),
  error_message: null,
  rolled_back_to: null,
};

const deploying = {
  deployment_id: "dep-2",
  environment: "staging",
  version: "1.3.0-rc1",
  status: "deploying" as const,
  created_at: new Date(Date.now() - 60_000).toISOString(),
  error_message: null,
  rolled_back_to: null,
};

const failed = {
  deployment_id: "dep-3",
  environment: "production",
  version: "1.2.1",
  status: "failed" as const,
  created_at: new Date(Date.now() - 7_200_000).toISOString(),
  error_message: "health check timeout",
  rolled_back_to: null,
};

const rolledBack = {
  deployment_id: "dep-4",
  environment: "production",
  version: "1.1.0",
  status: "rolled_back" as const,
  created_at: new Date(Date.now() - 86_400_000).toISOString(),
  error_message: null,
  rolled_back_to: "1.0.5",
};

const envs = ["staging", "production"];

describe("DeploymentTrackerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <DeploymentTrackerCard deployments={[deployed]} appName="My App" environments={envs} />,
    );
    expect(container.textContent).toContain("Deployments");
    expect(container.textContent).toContain("My App");
  });

  it("renders environment names", () => {
    const { container } = render(
      <DeploymentTrackerCard deployments={[deployed]} appName="App" environments={envs} />,
    );
    expect(container.textContent).toContain("staging");
    expect(container.textContent).toContain("production");
  });

  it("shows deployed version in environment row", () => {
    const { container } = render(
      <DeploymentTrackerCard deployments={[deployed]} appName="App" environments={envs} />,
    );
    expect(container.textContent).toContain("1.2.0");
    expect(container.textContent).toContain("Deployed");
  });

  it("shows in-progress badge for deploying", () => {
    const { container } = render(
      <DeploymentTrackerCard deployments={[deploying]} appName="App" environments={envs} />,
    );
    expect(container.textContent).toContain("1 in progress");
    expect(container.textContent).toContain("Deploying");
  });

  it("shows failed badge and error message", () => {
    const { container } = render(
      <DeploymentTrackerCard deployments={[failed]} appName="App" environments={envs} />,
    );
    expect(container.textContent).toContain("1 failed");
    expect(container.textContent).toContain("health check timeout");
  });

  it("shows rollback target version", () => {
    const { container } = render(
      <DeploymentTrackerCard deployments={[rolledBack]} appName="App" environments={envs} />,
    );
    expect(container.textContent).toContain("Rolled Back");
    expect(container.textContent).toContain("1.0.5");
  });

  it("shows no deployments for empty environment", () => {
    const { container } = render(
      <DeploymentTrackerCard
        deployments={[deployed]}
        appName="App"
        environments={["dev", "production"]}
      />,
    );
    expect(container.textContent).toContain("No deployments");
  });

  it("renders recent activity section", () => {
    const { container } = render(
      <DeploymentTrackerCard
        deployments={[deployed, deploying, failed]}
        appName="App"
        environments={envs}
      />,
    );
    expect(container.textContent).toContain("Recent Activity");
  });

  it("renders status icons", () => {
    const { container } = render(
      <DeploymentTrackerCard deployments={[deployed, failed]} appName="App" environments={envs} />,
    );
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("❌");
  });

  it("shows latest version per environment", () => {
    const olderProd = {
      ...deployed,
      deployment_id: "dep-old",
      version: "1.0.0",
      created_at: new Date(Date.now() - 86_400_000).toISOString(),
    };
    const newerProd = {
      ...deployed,
      deployment_id: "dep-new",
      version: "1.5.0",
      created_at: new Date(Date.now() - 1000).toISOString(),
    };
    const { container } = render(
      <DeploymentTrackerCard
        deployments={[olderProd, newerProd]}
        appName="App"
        environments={envs}
      />,
    );
    // The environment row should show the latest version
    expect(container.textContent).toContain("1.5.0");
  });
});
