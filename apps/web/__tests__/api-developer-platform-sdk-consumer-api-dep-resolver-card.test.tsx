import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DependencyResolverCard from "../src/components/api-developer-platform-sdk-consumer-api-dep-resolver-card";

describe("DependencyResolverCard", () => {
  it("renders title and nodes", () => {
    const { container } = render(<DependencyResolverCard />);
    expect(container.textContent).toContain("Dependency Resolver");
    expect(container.textContent).toContain("auth-service");
    expect(container.textContent).toContain("order-service");
  });

  it("shows dependency info", () => {
    const { container } = render(<DependencyResolverCard />);
    expect(container.textContent).toContain("depends on:");
    expect(container.textContent).toContain("1 root node");
    expect(container.textContent).toContain("4 total");
  });
});
