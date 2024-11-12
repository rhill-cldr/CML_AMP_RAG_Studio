import { Configuration } from "./api/configuration";

const basePath =
  process.env.REACT_APP_API_BASE_PATH ?? "http://localhost:8000/api/v1";

const config = new Configuration({
  basePath: basePath,
});

export default config;
