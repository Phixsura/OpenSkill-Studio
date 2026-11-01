import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperSandboxCard from "../src/components/api-developer-sandbox-card";

const sandboxes = [
  { sandbox_id: "sb1", developer_id: "alice", base_url: "https://sb1.api.dev", request_count: 150, active: true },
  { sandbox_id: "sb2", developer_id: "bob", base_url: "https://sb2.api.dev", request_count: 0, active: false },
];

describe("APIDeveloperSandboxCard", () => {
  it("shows sandboxes", () => {
    const { container } = render(<APIDeveloperSandboxCard sandboxes={sandboxes} appName="App" />);
    expect(container.textContent).toContain("Dev Sandboxes");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("150 reqs");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperSandboxCard sandboxes={[]} appName="App" />);
    expect(container.textContent).toContain("No sandboxes");
  });
});
