// Pure unit tests for the workflow editor conversion functions.
// Round-trip invariant: toDefinition(def, ...toReactFlow(def)) preserves
// steps/edges; ui.positions round to integers.

import { describe, it, expect } from "vitest";

import {
  applyStepUpdate,
  autoLayout,
  toDefinition,
  toReactFlow,
} from "@/components/workflow-editor/convert";
import { COERCIBLE, type StepDef, type WorkflowDefinition } from "@/components/workflow-editor/types";

function sampleDefinition(): WorkflowDefinition {
  return {
    schema_version: 1,
    inputs: [{ key: "topic", type: "text", required: true }],
    outputs: [{ key: "final", type: "image", from_step: "generate", from_port: "result" }],
    steps: [
      {
        id: "write_prompt",
        type: "prompt_template",
        name: "Build prompt",
        config: { template: "Photo of {{inputs.topic}}" },
        inputs: [],
        outputs: [{ port: "prompt", type: "prompt" }],
      },
      {
        id: "generate",
        type: "provider_action",
        name: "Generate",
        config: { capability: "image_generation", binding_mode: "auto" },
        inputs: [{ port: "prompt", type: "prompt" }],
        outputs: [{ port: "result", type: "image" }],
      },
    ],
    edges: [
      {
        id: "e1",
        from_step: "write_prompt",
        from_port: "prompt",
        to_step: "generate",
        to_port: "prompt",
      },
    ],
    ui: { positions: { write_prompt: [10, 20], generate: [300, 20] } },
  };
}

describe("toReactFlow", () => {
  it("produces nodes with positions from the ui block", () => {
    const { nodes, edges } = toReactFlow(sampleDefinition());
    expect(nodes).toHaveLength(2);
    const wp = nodes.find((n) => n.id === "write_prompt");
    expect(wp?.position).toEqual({ x: 10, y: 20 });
    expect(wp?.type).toBe("stepNode");
    expect(wp?.data.step.name).toBe("Build prompt");
    expect(edges).toHaveLength(1);
    expect(edges[0]).toMatchObject({
      id: "e1",
      source: "write_prompt",
      target: "generate",
      sourceHandle: "prompt",
      targetHandle: "prompt",
    });
  });

  it("falls back to index-based positions when ui block is empty", () => {
    const def = sampleDefinition();
    def.ui = {};
    const { nodes } = toReactFlow(def);
    expect(nodes[0]?.position).toEqual({ x: 0, y: 80 });
    expect(nodes[1]?.position).toEqual({ x: 280, y: 80 });
  });
});

describe("toDefinition round-trip", () => {
  it("preserves steps, edges and positions through a full round trip", () => {
    const original = sampleDefinition();
    const { nodes, edges } = toReactFlow(original);
    const roundTripped = toDefinition(original, nodes, edges);

    expect(roundTripped.steps).toEqual(original.steps);
    expect(roundTripped.edges).toEqual(original.edges);
    expect(roundTripped.inputs).toEqual(original.inputs);
    expect(roundTripped.outputs).toEqual(original.outputs);
    expect(roundTripped.ui.positions).toEqual(original.ui.positions);
  });

  it("rounds fractional node positions to integers", () => {
    const original = sampleDefinition();
    const { nodes, edges } = toReactFlow(original);
    const first = nodes[0];
    if (!first) throw new Error("expected a node");
    first.position = { x: 10.7, y: 19.2 };
    const def = toDefinition(original, nodes, edges);
    expect(def.ui.positions?.write_prompt).toEqual([11, 19]);
  });

  it("generates deterministic ids for new React Flow edges", () => {
    const original = sampleDefinition();
    const { nodes, edges } = toReactFlow(original);
    edges.push({
      id: "xy-edge__generate-result", // RF-generated id → replaced
      source: "generate",
      target: "write_prompt",
      sourceHandle: "result",
      targetHandle: "loop",
    });
    const def = toDefinition(original, nodes, edges);
    const newEdge = def.edges.find((e) => e.from_step === "generate");
    // '.'-joined: unambiguous since ids/ports contain '_' but never '.'
    expect(newEdge?.id).toBe("e_generate.result.write_prompt.loop");
  });

  it("drops steps whose nodes were removed", () => {
    const original = sampleDefinition();
    const { nodes, edges } = toReactFlow(original);
    const remaining = nodes.filter((n) => n.id !== "generate");
    const def = toDefinition(original, remaining, []);
    expect(def.steps.map((s) => s.id)).toEqual(["write_prompt"]);
    expect(def.edges).toEqual([]);
  });
});

describe("autoLayout", () => {
  it("assigns positions to every step", () => {
    const def = sampleDefinition();
    def.ui = {};
    const laid = autoLayout(def);
    expect(Object.keys(laid.ui.positions ?? {})).toEqual(
      expect.arrayContaining(["write_prompt", "generate"]),
    );
    for (const pos of Object.values(laid.ui.positions ?? {})) {
      expect(Number.isInteger(pos[0])).toBe(true);
      expect(Number.isInteger(pos[1])).toBe(true);
    }
  });

  it("does not mutate steps or edges", () => {
    const def = sampleDefinition();
    const laid = autoLayout(def);
    expect(laid.steps).toEqual(def.steps);
    expect(laid.edges).toEqual(def.edges);
  });
});

describe("applyStepUpdate — positional rename detection", () => {
  // Step with two input ports 'in' and 'in2', an edge feeding each.
  function twoPortDefinition(): WorkflowDefinition {
    return {
      schema_version: 1,
      inputs: [],
      outputs: [],
      steps: [
        {
          id: "src",
          type: "prompt_template",
          name: "Source",
          config: {},
          inputs: [],
          outputs: [
            { port: "out1", type: "text" },
            { port: "out2", type: "text" },
          ],
        },
        {
          id: "sink",
          type: "provider_action",
          name: "Sink",
          config: {},
          inputs: [
            { port: "in", type: "text" },
            { port: "in2", type: "text" },
          ],
          outputs: [],
        },
      ],
      edges: [
        { id: "e1", from_step: "src", from_port: "out1", to_step: "sink", to_port: "in" },
        { id: "e2", from_step: "src", from_port: "out2", to_step: "sink", to_port: "in2" },
      ],
      ui: {},
    };
  }

  it("rewrites edges on a simple rename a→b", () => {
    const def = twoPortDefinition();
    const sink = def.steps[1] as StepDef;
    const next = applyStepUpdate(def, {
      ...sink,
      inputs: [
        { port: "in", type: "text" },
        { port: "in3", type: "text" },
      ],
    });
    expect(next.edges).toHaveLength(2);
    expect(next.edges.find((e) => e.id === "e2")?.to_port).toBe("in3");
    expect(next.edges.find((e) => e.id === "e1")?.to_port).toBe("in");
  });

  it("never misroutes the sibling's edge when a collision is committed directly", () => {
    // Round 18: the old contract PARKED the renamed port's edge onto the
    // colliding sibling name ('rename in2→in while in exists'), which
    // MISROUTED data (both edges feeding one port — fan-in error on a port
    // the user never touched, or silently wrong data). Collisions are now
    // blocked upstream (PortNameInput holds the draft locally until unique),
    // and detectPortRename's TO-collision guard is defense-in-depth for
    // direct callers: no rename is applied, the sibling's edge is NEVER
    // touched, and the vanished port's edge is visibly disconnected rather
    // than silently rerouted.
    let def = twoPortDefinition();
    const sink = () => def.steps.find((s) => s.id === "sink") as StepDef;
    def = applyStepUpdate(def, {
      ...sink(),
      inputs: [
        { port: "in", type: "text" },
        { port: "in", type: "text" }, // direct collision commit
      ],
    });
    // Sibling's edge intact and NOT duplicated onto the colliding port
    expect(def.edges.filter((e) => e.to_port === "in")).toHaveLength(1);
    expect(def.edges.find((e) => e.id === "e1")?.to_port).toBe("in");
    // The renamed-away port's edge is dropped (visible disconnect), never
    // misrouted onto the sibling
    expect(def.edges.find((e) => e.id === "e2")).toBeUndefined();
  });

  it("rewrites the edge on a clean rename that the PortNameInput commits", () => {
    // The REAL keystroke flow after round 18: 'in2' → (collision 'in' held
    // locally, never committed) → 'in3' commits as one clean positional
    // rename. The edge follows the rename; the sibling is untouched.
    let def = twoPortDefinition();
    const sink = () => def.steps.find((s) => s.id === "sink") as StepDef;
    def = applyStepUpdate(def, {
      ...sink(),
      inputs: [
        { port: "in", type: "text" },
        { port: "in3", type: "text" },
      ],
    });
    expect(def.edges).toHaveLength(2);
    expect(def.edges.find((e) => e.id === "e1")?.to_port).toBe("in");
    expect(def.edges.find((e) => e.id === "e2")?.to_port).toBe("in3");
  });

  it("keeps an in-progress workflow output row (from_port: '') across step edits", () => {
    const def = twoPortDefinition();
    def.outputs = [
      { key: "done", type: "text", from_step: "src", from_port: "out1" },
      // "Add output" creates this shape before the user picks a port
      { key: "output_2", type: "image", from_step: "src", from_port: "" },
    ];
    const src = def.steps[0] as StepDef;
    const next = applyStepUpdate(def, { ...src, name: "Renamed source" });
    expect(next.outputs).toHaveLength(2);
    expect(next.outputs.find((o) => o.key === "output_2")?.from_port).toBe("");
    expect(next.outputs.find((o) => o.key === "done")?.from_port).toBe("out1");
  });
});

describe("COERCIBLE matrix", () => {
  it("allows identity and prompt↔text only", () => {
    expect(COERCIBLE.text).toContain("prompt");
    expect(COERCIBLE.prompt).toContain("text");
    expect(COERCIBLE.image).toEqual(["image"]);
    expect(COERCIBLE.text).not.toContain("image");
    expect(COERCIBLE.image).not.toContain("prompt");
    expect(COERCIBLE.video).toEqual(["video"]);
  });
});
