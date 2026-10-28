import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import StateMachineCard from "../src/components/state-machine-card";

const states = ["draft", "review", "approved", "rejected"];
const transitions = [
  { from_state: "draft", to_state: "review", event: "submit" },
  { from_state: "review", to_state: "approved", event: "approve" },
  { from_state: "review", to_state: "rejected", event: "reject" },
];
const entities = [
  { entity_id: "doc-1", current_state: "review", transition_count: 1 },
  { entity_id: "doc-2", current_state: "approved", transition_count: 2 },
  { entity_id: "doc-3", current_state: "draft", transition_count: 0 },
];

describe("StateMachineCard", () => {
  it("renders header and machine id", () => {
    const { container } = render(
      <StateMachineCard
        machineId="approval"
        states={states}
        transitions={transitions}
        entities={entities}
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("State Machine");
    expect(container.textContent).toContain("approval");
  });

  it("shows entity count", () => {
    const { container } = render(
      <StateMachineCard
        machineId="m1"
        states={states}
        transitions={transitions}
        entities={entities}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("3 entities");
  });

  it("renders state names with counts", () => {
    const { container } = render(
      <StateMachineCard
        machineId="m1"
        states={states}
        transitions={transitions}
        entities={entities}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("review");
    expect(container.textContent).toContain("(1)");
    expect(container.textContent).toContain("approved");
  });

  it("renders transitions with events", () => {
    const { container } = render(
      <StateMachineCard
        machineId="m1"
        states={states}
        transitions={transitions}
        entities={entities}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("draft");
    expect(container.textContent).toContain("→");
    expect(container.textContent).toContain("submit");
    expect(container.textContent).toContain("approve");
  });

  it("renders entity list with states", () => {
    const { container } = render(
      <StateMachineCard
        machineId="m1"
        states={states}
        transitions={transitions}
        entities={entities}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("doc-1");
    expect(container.textContent).toContain("1 transitions");
  });

  it("shows overflow for many entities", () => {
    const manyEntities = Array.from({ length: 8 }, (_, i) => ({
      entity_id: `e-${i}`,
      current_state: "draft",
      transition_count: 0,
    }));
    const { container } = render(
      <StateMachineCard
        machineId="m1"
        states={states}
        transitions={transitions}
        entities={manyEntities}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("+3 more");
  });
});
