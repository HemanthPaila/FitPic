import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

export const predictFit = (data) => API.post("/fit", data);
export const tryOn = (formData) => API.post("/tryon", formData);
