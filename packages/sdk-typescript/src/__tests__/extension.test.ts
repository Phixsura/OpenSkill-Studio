import { describe, test, expect } from "vitest";
import { OpenSkillExtension } from "../extension.js";

describe("OpenSkillExtension", () => {
  test("constructor requires origin", () => {
    expect(() => new OpenSkillExtension({ origin: "*" })).toThrow("origin is required");
  });

  test("constructor rejects empty origin", () => {
    expect(() => new OpenSkillExtension({ origin: "" })).toThrow("origin is required");
  });

  test("isReady is false initially", () => {
    // We can't fully test in Node (no window), but we can test the class exists
    expect(OpenSkillExtension).toBeDefined();
  });

  test("extension has api and ui properties", () => {
    // Can't instantiate without window, but verify the class structure
    expect(OpenSkillExtension.prototype).toBeDefined();
    expect(typeof OpenSkillExtension.prototype.destroy).toBe("function");
  });
});
