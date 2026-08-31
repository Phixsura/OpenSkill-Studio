// Invariant tests for editor logic against the backend validator contract
// (apps/api/app/schemas/workflow_definition.py):
// - step ids / port names / io keys: ^[a-z][a-z0-9_]{0,63}$, unique
// - single port namespace per step (inputs + outputs share it)
// - edges/outputs must reference existing steps+ports
// The editor must never SAVE a violating definition when the user's actions
// were individually legal, and must never corrupt state on legal sequences.

import { describe, it, expect } from "vitest";

import { applyStepUpdate, toDefinition, toReactFlow } from "@/components/workflow-editor/convert";
import {
  normalizeDefinition,
  normalizePosition,
  sanitizeKey,
  type StepDef,
  type WorkflowDefinition,
} from "@/components/workflow-editor/types";

function def2(): WorkflowDefinition {
  return {
    schema_version: 1,
    inputs: [{ key: "topic", type: "text", required: true }],
    outputs: [{ key: "final", type: "image", from_step: "gen", from_port: "result" }],
    steps: [
      {
        id: "prep",
        type: "prompt_template",
        name: "Prep",
        config: { template: "x" },
        inputs: [],
        outputs: [{ port: "prompt", type: "prompt" }],
      },
      {
        id: "gen",
        type: "provider_action",
        name: "Gen",
        config: { capability: "image_generation" },
        inputs: [{ port: "prompt", type: "prompt" }],
        outputs: [{ port: "result", type: "image" }],
      },
    ],
    edges: [
      { id: "e1", from_step: "prep", from_port: "prompt", to_step: "gen", to_port: "prompt" },
    ],
    ui: {},
  };
}

describe("normalizeDefinition (load-time hardening)", () => {
  it("fills missing per-step config/inputs/outputs (backend stores RAW dict)", () => {
    const raw = {
      schema_version: 1,
      steps: [{ id: "a", type: "instruction", name: "A" }], // no config/inputs/outputs
    };
    const def = normalizeDefinition(raw);
    expect(def.steps[0]?.inputs).toEqual([]);
    expect(def.steps[0]?.outputs).toEqual([]);
    expect(def.steps[0]?.config).toEqual({});
    // and the canvas conversion must not throw on it
    expect(() => toReactFlow(def)).not.toThrow();
  });

  it("drops garbage ui.positions instead of producing NaN node positions", () => {
    const raw = {
      steps: [{ id: "a", type: "instruction", name: "A", config: {}, inputs: [], outputs: [] }],
      ui: { positions: { a: "not-a-tuple", ghost: [1, 2], b: [null, undefined] } },
    };
    const def = normalizeDefinition(raw);
    expect(def.ui.positions).toEqual({ ghost: [1, 2] });
    const { nodes } = toReactFlow(def);
    expect(Number.isFinite(nodes[0]?.position.x)).toBe(true);
    expect(Number.isFinite(nodes[0]?.position.y)).toBe(true);
  });

  it("tolerates entirely non-object input", () => {
    for (const junk of [null, undefined, 42, "x", []]) {
      const def = normalizeDefinition(junk);
      expect(def.steps).toEqual([]);
      expect(def.edges).toEqual([]);
    }
  });

  it("preserves unknown extra keys inside ui", () => {
    const def = normalizeDefinition({ ui: { positions: {}, zoom: 1.5 } });
    expect((def.ui as Record<string, unknown>).zoom).toBe(1.5);
  });
});

describe("normalizePosition", () => {
  it("accepts numeric-ish tuples and rejects everything else", () => {
    expect(normalizePosition([1, 2])).toEqual([1, 2]);
    expect(normalizePosition(["3", "4"])).toEqual([3, 4]); // JSON round-trips may stringify
    expect(normalizePosition([NaN, 1])).toBeNull();
    expect(normalizePosition([Infinity, 1])).toBeNull();
    expect(normalizePosition([1])).toBeNull();
    expect(normalizePosition("x")).toBeNull();
    expect(normalizePosition(null)).toBeNull();
  });
});

describe("sanitizeKey (backend regex ^[a-z][a-z0-9_]{0,63}$)", () => {
  it("strips leading digits/underscores that the old sanitizer let through", () => {
    // Old sanitizer: "2nd_pass" → "2nd_pass" (starts with digit → backend WF_INVALID_PORT)
    expect(sanitizeKey("2nd_pass")).toBe("nd_pass");
    expect(sanitizeKey("_hidden")).toBe("hidden");
    expect(sanitizeKey("--x")).toBe("x");
  });
  it("lowercases and replaces illegal chars", () => {
    // "My Key!" → lowercase "my key!" → replace → "my_key_" (starts with 'm', legal)
    expect(sanitizeKey("My Key!")).toBe("my_key_");
  });
  it("keeps a legal key unchanged", () => {
    expect(sanitizeKey("hero_image")).toBe("hero_image");
  });
  it("caps at 64 chars", () => {
    expect(sanitizeKey("a".repeat(100))).toHaveLength(64);
  });
  it("can return empty (caller shows field-level invalid state; backend rejects)", () => {
    expect(sanitizeKey("123")).toBe("");
    expect(sanitizeKey("___")).toBe("");
  });
});

describe("applyStepUpdate — port rename cascades", () => {
  it("REWRITES edges and workflow outputs on a 1:1 output-port rename", () => {
    const def = def2();
    const gen = def.steps[1] as StepDef;
    const renamed: StepDef = {
      ...gen,
      outputs: [{ port: "artwork", type: "image" }], // result → artwork
    };
    const next = applyStepUpdate(def, renamed);
    // The workflow output must FOLLOW the rename, not be dropped
    expect(next.outputs).toEqual([
      { key: "final", type: "image", from_step: "gen", from_port: "artwork" },
    ]);
    // No edges referenced gen's outputs, edge untouched
    expect(next.edges).toEqual(def.edges);
  });

  it("REWRITES edges on a 1:1 input-port rename (each keystroke is a rename)", () => {
    const def = def2();
    const gen = def.steps[1] as StepDef;
    // simulate one keystroke: "prompt" → "promptx"
    const next = applyStepUpdate(def, {
      ...gen,
      inputs: [{ port: "promptx", type: "prompt" }],
    });
    expect(next.edges).toEqual([
      { id: "e1", from_step: "prep", from_port: "prompt", to_step: "gen", to_port: "promptx" },
    ]);
  });

  it("survives a full character-by-character rename with the edge intact", () => {
    let def = def2();
    const target = () => def.steps.find((s) => s.id === "gen") as StepDef;
    // "prompt" → "p" (backspaces) → then typing "icture"
    const sequence = [
      "promp",
      "prom",
      "pro",
      "pr",
      "p",
      "pi",
      "pic",
      "pict",
      "pictu",
      "pictur",
      "picture",
    ];
    for (const name of sequence) {
      def = applyStepUpdate(def, {
        ...target(),
        inputs: [{ port: name, type: "prompt" }],
      });
    }
    expect(def.edges).toHaveLength(1);
    expect(def.edges[0]?.to_port).toBe("picture");
  });

  it("DROPS edges/outputs on pure port removal (not a rename)", () => {
    const def = def2();
    const gen = def.steps[1] as StepDef;
    const next = applyStepUpdate(def, { ...gen, inputs: [], outputs: [] });
    expect(next.edges).toEqual([]);
    expect(next.outputs).toEqual([]);
  });

  it("does not rewrite when multiple ports change at once (ambiguous)", () => {
    const def = def2();
    const gen = def.steps[1] as StepDef;
    const next = applyStepUpdate(def, {
      ...gen,
      outputs: [
        { port: "a", type: "image" },
        { port: "b", type: "image" },
      ],
    });
    // "result" gone, two added — ambiguous, output dropped (never dangles)
    expect(next.outputs).toEqual([]);
  });

  it("leaves other steps' edges alone", () => {
    const def = def2();
    const prep = def.steps[0] as StepDef;
    const next = applyStepUpdate(def, { ...prep, name: "Renamed display name" });
    expect(next.edges).toEqual(def.edges);
    expect(next.outputs).toEqual(def.outputs);
  });
});

describe("toDefinition edge-id generation", () => {
  it("keeps distinct generated ids for edges differing only in port grouping", () => {
    // '.'-join is unambiguous because ids/ports never contain '.':
    // (a, b_c) vs (a_b, c) must NOT collide
    const def: WorkflowDefinition = {
      schema_version: 1,
      inputs: [],
      outputs: [],
      steps: [
        {
          id: "a",
          type: "instruction",
          name: "",
          config: {},
          inputs: [],
          outputs: [{ port: "b_c", type: "text" }],
        },
        {
          id: "a_b",
          type: "instruction",
          name: "",
          config: {},
          inputs: [],
          outputs: [{ port: "c", type: "text" }],
        },
        {
          id: "z",
          type: "instruction",
          name: "",
          config: {},
          inputs: [
            { port: "p", type: "text" },
            { port: "q", type: "text" },
          ],
          outputs: [],
        },
      ],
      edges: [],
      ui: {},
    };
    const { nodes } = toReactFlow(def);
    const rfEdges = [
      { id: "xy-edge__1", source: "a", target: "z", sourceHandle: "b_c", targetHandle: "p" },
      { id: "xy-edge__2", source: "a_b", target: "z", sourceHandle: "c", targetHandle: "q" },
    ];
    const out = toDefinition(def, nodes, rfEdges);
    const ids = out.edges.map((e) => e.id);
    expect(new Set(ids).size).toBe(2);
    expect(ids[0]).not.toBe(ids[1]);
  });

  it("round-trips a definition with zero edges and zero ports", () => {
    const def: WorkflowDefinition = {
      schema_version: 1,
      inputs: [],
      outputs: [],
      steps: [
        { id: "solo", type: "instruction", name: "Solo", config: {}, inputs: [], outputs: [] },
      ],
      edges: [],
      ui: {},
    };
    const { nodes, edges } = toReactFlow(def);
    const rt = toDefinition(def, nodes, edges);
    expect(rt.steps).toEqual(def.steps);
    expect(rt.edges).toEqual([]);
  });

  it("prunes ui.positions entries for steps that no longer exist", () => {
    const def = def2();
    def.ui = { positions: { prep: [0, 0], gen: [100, 0], ghost_step: [999, 999] } };
    const { nodes, edges } = toReactFlow(def);
    const rt = toDefinition(def, nodes, edges);
    expect(rt.ui.positions).not.toHaveProperty("ghost_step");
    expect(rt.ui.positions).toHaveProperty("prep");
  });

  it("preserves backend-supplied duplicate-free edge ids verbatim", () => {
    const def = def2();
    const { nodes, edges } = toReactFlow(def);
    const rt = toDefinition(def, nodes, edges);
    expect(rt.edges[0]?.id).toBe("e1");
  });
});
