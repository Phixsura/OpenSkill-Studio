import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CommandCenterCard from "../src/components/api-developer-platform-sdk-consumer-api-command-center-card";

describe("CommandCenterCard", () => {
  it("renders title and status", () => {
    const { container } = render(<CommandCenterCard />);
    expect(container.textContent).toContain("Command Center");
    expect(container.textContent).toContain("all operational");
    expect(container.textContent).toContain("pair #1100");
  });

  it("shows metrics and health", () => {
    const { container } = render(<CommandCenterCard />);
    expect(container.textContent).toContain("250");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("1.3M requests/24h");
    expect(container.textContent).toContain("0.3% error rate");
  });
});
