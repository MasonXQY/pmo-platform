import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { fetchProjects } from "../api/projects";
import { Project } from "../types/project";

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    fetchProjects().then(setProjects);
  }, []);

  return (
    <Layout>
      <h2 className="text-2xl font-semibold mb-4">Projects</h2>

      <div className="grid gap-4">
        {projects.map((project) => (
          <div key={project.id} className="bg-white p-4 shadow rounded">
            <h3 className="text-lg font-bold">{project.name}</h3>
            <p>Status: {project.status}</p>
            <p>Health: {project.health_score}</p>
          </div>
        ))}
      </div>
    </Layout>
  );
}
