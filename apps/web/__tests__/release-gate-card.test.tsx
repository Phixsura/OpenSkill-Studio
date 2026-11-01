import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ReleaseGateCard from "../src/components/release-gate-card";

const gates = [
  { gate_id: "tests", name: "Unit Tests", required: true, status: "passed" as const, message: "" },
  {
    gate_id: "coverage",
    name: "Code Coverage",
    required: true,
    status: "passed" as const,
    message: "92%",
  },
  {
    gate_id: "review",
    name: "Peer Review",
    required: true,
    status: "failed" as const,
    message: "Pending approval",
  },
  {
    gate_id: "docs",
    name: "Docs Updated",
    required: false,
    status: "pending" as const,
    message: "",
  },
];

describe("ReleaseGateCard", () => {
  it("renders header with version", () => {
    const { container } = render(
      <ReleaseGateCard version="2.0.0" gates={gates} approved={false} appName="My App" />,
    );
    expect(container.textContent).toContain("Release Gates");
    expect(container.textContent).toContain("v2.0.0");
  });

  it("shows passed count when not approved", () => {
    const { container } = render(
      <ReleaseGateCard version="2.0.0" gates={gates} approved={false} appName="App" />,
    );
    expect(container.textContent).toContain("2/4 passed");
  });

  it("shows approved badge", () => {
    const { container } = render(
      <ReleaseGateCard version="2.0.0" gates={gates} approved={true} appName="App" />,
    );
    expect(container.textContent).toContain("Approved");
  });

  it("renders gate names", () => {
    const { container } = render(
      <ReleaseGateCard version="1.0.0" gates={gates} approved={false} appName="App" />,
    );
    expect(container.textContent).toContain("Unit Tests");
    expect(container.textContent).toContain("Peer Review");
  });

  it("shows optional label", () => {
    const { container } = render(
      <ReleaseGateCard version="1.0.0" gates={gates} approved={false} appName="App" />,
    );
    expect(container.textContent).toContain("optional");
  });

  it("shows gate messages", () => {
    const { container } = render(
      <ReleaseGateCard version="1.0.0" gates={gates} approved={false} appName="App" />,
    );
    expect(container.textContent).toContain("92%");
    expect(container.textContent).toContain("Pending approval");
  });

  it("shows status icons", () => {
    const { container } = render(
      <ReleaseGateCard version="1.0.0" gates={gates} approved={false} appName="App" />,
    );
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("✕");
    expect(container.textContent).toContain("○");
  });
});
