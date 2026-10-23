import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusIndicator } from "@/components/status-indicator";

describe("StatusIndicator", () => {
  it("renders online", () => {
    const { container } = render(
      <StatusIndicator status="online" label="Online" icon="🟢" color="green" appName="MyApp" isHealthy={true} />
    );
    expect(container.textContent).toContain("MyApp");
    expect(container.textContent).toContain("Online");
    expect(container.textContent).toContain("🟢");
  });
});
