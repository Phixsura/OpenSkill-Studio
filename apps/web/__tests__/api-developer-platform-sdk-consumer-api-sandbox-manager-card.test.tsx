import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SandboxManagerCard from "../src/components/api-developer-platform-sdk-consumer-api-sandbox-manager-card";

describe("SandboxManagerCard", () => {
  it("renders title and sandboxes", () => {
    const { container } = render(<SandboxManagerCard />);
    expect(container.textContent).toContain("Sandbox Manager");
    expect(container.textContent).toContain("Integration Test");
    expect(container.textContent).toContain("Load Test");
  });

  it("shows status and active count", () => {
    const { container } = render(<SandboxManagerCard />);
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("paused");
    expect(container.textContent).toContain("2 active sandboxes");
  });
});
