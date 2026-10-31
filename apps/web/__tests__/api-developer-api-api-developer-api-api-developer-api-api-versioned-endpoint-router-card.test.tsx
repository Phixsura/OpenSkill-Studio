import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiVersionedEndpointRouterCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-versioned-endpoint-router-card";

const routes = [{ endpoint: "/api/users", versions: { v1: "h1", v2: "h2" }, default_version: "v2", request_counts: { v1: 500, v2: 5000 } }];

describe("Card", () => {
  it("shows versioned routes", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiVersionedEndpointRouterCard routes={routes} appName="App" />);
    expect(container.textContent).toContain("Versioned Router");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("v1: 500");
    expect(container.textContent).toContain("v2: 5000");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiVersionedEndpointRouterCard routes={[]} appName="App" />);
    expect(container.textContent).toContain("No versioned routes");
  });
});
