import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-sandbox-environment-card";

describe("SandboxEnvironmentCard", () => {
  it("shows sandboxes", () => {
    const sandboxes = [{ sandbox_id: "sb-1", consumer_id: "c1", status: "active", request_count: 500, request_limit: 10000, data_seeded: true, reset_count: 2 }];
    const { container } = render(<Card sandboxes={sandboxes} appName="App" />);
    expect(container.textContent).toContain("Sandboxes");
    expect(container.textContent).toContain("c1 / sb-1");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("seeded");
  });
  it("shows empty", () => {
    const { container } = render(<Card sandboxes={[]} appName="App" />);
    expect(container.textContent).toContain("No sandboxes");
  });
});
