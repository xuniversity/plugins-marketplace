import { requestClient } from '#/api/request';

export interface FileUploadResponse {
  filename?: string;
  path?: string;
  url: string;
}

export interface FileInfoResponse {
  contentType?: string;
  filename?: string;
  size?: number;
  url: string;
}

export async function uploadFile(data: FormData) {
  return requestClient.post<FileUploadResponse>('/api/file/upload', data);
}

export async function getFileInfoApi(url: string) {
  return requestClient.get<FileInfoResponse>('/api/file/info', {
    params: { url },
  });
}
