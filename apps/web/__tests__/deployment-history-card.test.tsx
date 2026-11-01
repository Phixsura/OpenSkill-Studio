import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DeploymentHistoryCard from "../src/components/deployment-history-card";

const deployments = [
  {
    deploy_id: "d1",
    version: "v2.1",
    commit_sha: "abc1234def",
    deployer: "alice",
    result: "success" as const,
    duration_seconds: 45.2,
  },
  {
    deploy_id: "d2",
    version: "v2.0",
    commit_sha: "xyz9876fed",
    deployer: "bob",
    result: "failure" as const,
    duration_seconds: 12.0,
  },
];

describe("DeploymentHistoryCard", () => {
  it("renders header and stats", () => {
    const { container } = render(
      <DeploymentHistoryCard deployments={deployments} successRate={80} appName="App" />,
    );
    expect(container.textContent).toContain("Deployment History");
    expect(container.textContent).toContain("2 deploys");
    expect(container.textContent).toContain("80% success");
  });

  it("shows versions and commits", () => {
    const { container } = render(
      <DeploymentHistoryCard deployments={deployments} successRate={50} appName="App" />,
    );
    expect(container.textContent).toContain("v2.1");
    expect(container.textContent).toContain("abc1234");
  });

  it("shows result badges and deployer", () => {
    const { container } = render(
      <DeploymentHistoryCard deployments={deployments} successRate={50} appName="App" />,
    );
    expect(container.textContent).toContain("success");
    expect(container.textContent).toContain("failure");
    expect(container.textContent).toContain("alice");
  });

  it("shows empty state", () => {
    const { container } = render(
      <DeploymentHistoryCard deployments={[]} successRate={100} appName="App" />,
    );
    expect(container.textContent).toContain("No deployments");
  });
});
