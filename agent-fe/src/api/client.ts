/**
 * API entrypoint — thin re-export of the Orval-generated client.
 *
 * Regenerate with `npm run generate` (backend must be running on :8000).
 */
export {
  listSessionsApiSessionsGet as listSessions,
  createSessionApiSessionsPost as createSession,
  getSessionApiSessionsSessionIdGet as getSession,
  deleteSessionApiSessionsSessionIdDelete as deleteSession,
  chatApiChatSessionIdPost as postChat,
} from './generated/aICertificateOperationsAgent'