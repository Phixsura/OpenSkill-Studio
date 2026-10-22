import { describe, test, expect } from "vitest";

describe("SDK exports", () => {
  test("OpenSkillClient is exported", async () => {
    const mod = await import("../index.js");
    expect(mod.OpenSkillClient).toBeDefined();
  });

  test("Error classes are exported", async () => {
    const mod = await import("../index.js");
    expect(mod.OpenSkillError).toBeDefined();
    expect(mod.ApiError).toBeDefined();
    expect(mod.AuthError).toBeDefined();
    expect(mod.NotFoundError).toBeDefined();
  });

  test("Extension SDK is importable", async () => {
    const mod = await import("../extension.js");
    expect(mod.OpenSkillExtension).toBeDefined();
  });
});
