import { defineConfig } from 'orval'

// Generate the API client from the backend OpenAPI schema.
// Usage: npm run generate  (backend must be running on :8000)
export default defineConfig({
  certAgent: {
    input: 'http://localhost:8000/openapi.json',
    output: {
      target: './src/api/generated',
      client: 'react-query',
      httpClient: 'axios',
      mock: false,
      clean: true,
      prettier: false,
      override: {
        mutator: {
          path: './src/api/mutator.ts',
          name: 'customInstance',
        },
        query: {
          useQuery: true,
          useMutation: true,
        },
        operations: {
          list_sessions_api_sessions_get: { name: 'listSessions' },
          create_session_api_sessions_post: { name: 'createSession' },
          get_session_api_sessions__session_id__get: { name: 'getSession' },
          delete_session_api_sessions__session_id__delete: {
            name: 'deleteSession',
          },
          chat_api_chat__session_id__post: { name: 'postChat' },
        },
      },
    },
  },
})