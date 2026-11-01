import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployHealthPanel } from "@/components/deploy-health-panel";
describe("DeployHealthPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployHealthPanel healthy={false} passed={1} failed={1} totalMs={5050} recommendation="rollback"
        checks={[
          { name: "http_200", passed: true, durationMs: 50 },
          { name: "db_connected", passed: false, durationMs: 5000 },
        ]} />
    );
    expect(container.textContent).toContain("UNHEALTHY");
    expect(container.textContent).toContain("5050ms");
    expect(container.textContent).toContain("rollback");
    expect(container.textContent).toContain("http_200");
    expect(container.textContent).toContain("db_connected");
  });
});
