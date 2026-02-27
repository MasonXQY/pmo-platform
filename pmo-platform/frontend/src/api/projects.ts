import { api } from "./client";
import { Project } from "../types/project";

export const fetchProjects = async (): Promise<Project[]> => {
  const response = await api.get("/projects");
  return response.data;
};
