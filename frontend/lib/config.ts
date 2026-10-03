/**
 * Centralized API & Environment Configuration
 *
 * For local development: defaults to http://127.0.0.1:8000
 * For production (Vercel): configured via NEXT_PUBLIC_API_URL environment variable.
 */

const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// Strip trailing slash if provided to prevent double slashes in endpoint paths
export const API_URL = rawApiUrl.replace(/\/+$/, "");

// Backwards-compatible alias
export const API_BASE = API_URL;
