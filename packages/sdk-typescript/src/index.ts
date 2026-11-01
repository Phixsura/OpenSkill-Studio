/**
 * @openskill/sdk — OpenSkill Platform SDK for TypeScript
 *
 * Build apps, connectors, and extensions for OpenSkill Studio.
 *
 * @example
 * ```ts
 * import { OpenSkillClient } from '@openskill/sdk';
 *
 * const client = new OpenSkillClient({
 *   apiKey: 'osk_app_...',
 *   baseUrl: 'https://api.openskill.dev',
 * });
 *
 * const cohorts = await client.cohorts.list({ limit: 10 });
 * ```
 */

export { OpenSkillClient, type ClientConfig } from "./client.js";
export {
  type App,
  type AppVersion,
  type AppInstallation,
  type DeveloperAccount,
  type ApiKey,
  type EventSubscription,
  type AutomationRule,
  type Manifest,
  type Permission,
  type AppCategory,
  type AppStatus,
  type AppVisibility,
} from "./types.js";
export { OpenSkillError, ApiError, AuthError, NotFoundError } from "./errors.js";
