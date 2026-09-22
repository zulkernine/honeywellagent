import axios from 'axios'
import type { AxiosRequestConfig, Canceler } from 'axios'

export const AXIOS_INSTANCE = axios.create({})

// Orval mutator: keeps generated calls relative ('/api/...') so the Vite dev
// proxy handles CORS-free localhost routing.
export const customInstance = <T>(
  config: AxiosRequestConfig,
): Promise<T> & { cancel: Canceler } => {
  const source = axios.CancelToken.source()
  const promise = AXIOS_INSTANCE({
    ...config,
    cancelToken: source.token,
  }).then(({ data }) => data as T) as Promise<T> & { cancel: Canceler }
  promise.cancel = () => {
    source.cancel('Query was cancelled')
  }
  return promise as unknown as Promise<T> & { cancel: Canceler }
}

export type ErrorType<ErrorData> = ErrorData
export type BodyType<BodyData> = BodyData

export default customInstance