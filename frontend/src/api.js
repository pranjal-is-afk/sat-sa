import axios from 'axios';

const api = axios.create({ baseURL: '/api', timeout: 60000 });

export const uploadFiles = (formData, onProgress) => 
  api.post('/ingest', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  });

export const runAnalysis = (batchId) =>
  api.post('/analyse', { batch_id: batchId });

export const getOverview = (batchId) =>
  api.get('/overview', { params: { batch_id: batchId } });

export const getEntities = (batchId, filters = {}) =>
  api.get('/entities', { params: { batch_id: batchId, ...filters } });

export const getEntity = (cseId, batchId) =>
  api.get(`/entity/${cseId}`, { params: { batch_id: batchId } });

export const getNegativeSpace = (batchId) =>
  api.get('/negative-space', { params: { batch_id: batchId } });

export const addNote = (batchId, cseId, note) =>
  api.post('/notes', { batch_id: batchId, cse_id: cseId, note });
