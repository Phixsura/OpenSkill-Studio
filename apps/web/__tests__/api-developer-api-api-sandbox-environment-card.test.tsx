import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiSandboxEnvironmentCard from "../src/components/api-developer-api-api-sandbox-environment-card";

const sandboxes = [
  { sandbox_id: "s1", name: "Dev Sandbox", base_url: "https://dev.api.com", status: "active", request_count: 150 },
  { sandbox_id: "s2", name: "QA Sandbox", base_url: "https://qa.api.com", status: "paused", request_count: 50 },
];

describe("APIDeveloperAPIApiSandboxEnvironmentCard", () => {
  it("shows sandboxes", () => {
    const { container } = render(<APIDeveloperAPIApiSandboxEnvironmentCard sandboxes={sandboxes} appName="App" />);
    expect(container.textContent).toContain("Sandbox Environments");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("Dev Sandbox");
    expect(container.textContent).toContain("https://dev.api.com");
    expect(container.textContent).toContain("150 reqs");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiSandboxEnvironmentCard sandboxes={[]} appName="App" />);
    expect(container.textContent).toContain("No sandboxes");
  });
});
